#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 09:26:05 2019

@author: rita

Flask app

"""

import regex, os, io, sys
from random import sample
import pandas as pd
import numpy as np 

from unidecode import unidecode

from flask import Flask, render_template, request, session, redirect, url_for, flash

import uuid
import time
from datetime import datetime as dt
from difflib import SequenceMatcher

from google.cloud import storage

from DatabaseConnector import _write_file, _read_file, _list_dir, _path_exists
from Contest import Contest
from ChatGPT import ChatGPT


app = Flask(__name__)
app.secret_key = b'_asfqwr54q3rfvcEQ@$'

## PATHS
root_path = os.path.dirname(os.path.dirname(__file__))
data_path = os.path.join(root_path, "data", "available_contests0.csv")
prompts_path = os.path.join(root_path, "data", "utils", "prompts.csv")
story_addons_path = os.path.join(root_path, "data", "utils", "story_addons.csv")
naked_bases_path = os.path.join(root_path, "data", "naked_bases.pkl")
bases_path = os.path.join(root_path, "data", "users", "all_rules.pkl")
accepted_contests_path = os.path.join(root_path, "data", "users", "user_rules.pkl")


## VARS
url = "https://www.escritores.org/concursos/concursos-1/concursos-cuento-relato"

prompts_df = _read_file(prompts_path)
prompts = dict(zip(prompts_df.tipo, prompts_df.prompt))



paths = {
    "data": data_path,
    "prompts": prompts_path,
    "contest_rules": bases_path,
    "story_addons": story_addons_path
         }


save_class = False
verbose = False
color_codes_wanted = {"human":"#9828bd", "chatgpt":"#ffcc33"}

chatGPT = ChatGPT()

contest = Contest(root_path)
contest.get_ruled_contests()


    
def chatgpt_restrict_checker(final_bases, restriction_cond, n_contests=10):
    n = 0
    accepted_contests = []
    for k, input_params in final_bases.items(): 
        cond_sending_add = input_params.get("direccion_de_envio", "") and regex.search(r"(\@|https:\/\/)", input_params.get("direccion_de_envio"))
        cond_date = dt.now().date() < input_params.get("fecha_de_vencimiento", dt.now().date())
        cond_extens0 = regex.search(r"novela|compilación|antología", input_params.get("genero"), regex.I) and not regex.search(r"[\,\;]", input_params.get("genero")) if input_params.get("genero") else False 
        cond_extens1 = regex.search(r"([4567890]+|[1230]{2,})\s(p\wgina|folio|cuartilla)s|([67890]|[12345]{2,})[\.\,\s]?000\spalabras", input_params.get("extension"), regex.I) if input_params.get("extension") else False
        cond_extens = cond_extens0 or cond_extens1
        if cond_sending_add and cond_date and not cond_extens:
            query_params = {}
            query_params["bases"] = input_params
            query_params["restricting_cond"] = restriction_cond
            chatgpt_restrictions = chatGPT.query_blank_slate(prompts.get("concurso_permitido").format(**query_params), model="gpt-4o-mini")
            cond0 = regex.search(r"(^No|(desafortunada|lamentable|desgraciada)mente|por\sdesgracia|no\scumpl((ir)?ías|[ae]s?))", chatgpt_restrictions, regex.I)
            if not cond0:
                accepted_contests.append(k)
                if n >= n_contests-1:
                    break
                n += 1
                        
    return accepted_contests


def generate_chatgpt_story(input_params):

    story = chatGPT.query_blank_slate(prompts.get("extraer_cuento").format(**input_params), model="gpt-4o-mini")
              
    cond1 = len(regex.findall(r"(\*{2,}[A-Z]\w*(\s\w+){,2}\:?\*{2,})|(\#+\s?[A-Z]\w+\:)", story)) <= 3
    cond2 = len(regex.findall(r"[\#\*]{2,}\s?(sinopsis|introducci\wn|desenlace|conclusi\wn|estructura|desarrollo|cl\wmax)", story, regex.I)) <= 2
    cond3 = len(regex.findall(r"[\#\*]{2,}\s?(parte|cap\wtulo|[ivx]+)\s?\d+", story, regex.I)) <= 3
    
    if not (cond1 and cond2 and cond3):
        story = chatGPT.query_blank_slate(prompts.get("extraer_cuento").format(**input_params), model="gpt-4o-mini")

    rex_cleaner = regex.compile("(^\W*(((Claro|Por\ssupuesto|A\scontinuación)\,\s)?(aquí\stienes|puedo\s\w+|te\spresento\s\w+)[^\.]+)?(t\wtul(ad)?o)?\W+|[\n\s]+$)", regex.I)
    story = regex.sub(rex_cleaner, "", story)
            
    cond_title0 = regex.search(r"(?<=^\W*(t\wtul(ad)?o|\w+\:)\W+)[^\n]+", story, regex.I)
    cond_title1 = regex.search(r"^\W*([A-Z]\w+(\W{1,3}\w+){,13}\W*)(?=\n+[A-Z][a-záéíóú]+\s([A-Z][a-záéíóú]+){,3}[a-záéíóú]{2,})", story)
    if cond_title0:
        story_title = regex.sub(r"(^\W+|[\s\n\*\#\-]+$)", "", cond_title0.group())
    elif cond_title1:
        story_title = regex.sub(r"(^\W+|[\s\n\*\#\-]+$)", "", cond_title1.group())
    else:
        story_title = ""        
        
    final_comments_re = r"\n\s*(\-{3,}|\W{2,}Fin((al)?\sdel\s([Aa]cto|[cC]uento|[rR]elato))?\W{2,})\s*\n(\W?[\w\s\:\,\:]+[\?\!\.]){1,3}$"
    final_comments_re1 = r'[\-\#\*]+[\s\n]*(\w+\W+){,35}(frases\shechas|expresiones\sidiom\wticas)(\w+\W+){,35}$'
    
    final_response = {}
    final_response["final_story"] = regex.sub(r"^\W+", "", 
                                            regex.sub(regex.compile(regex.escape(story_title)), "", 
                                                      regex.sub(r"(?<=\W)[\#\*]+Fin\W*$", "", 
                                                                regex.sub(final_comments_re1, "", 
                                                                          regex.sub(final_comments_re, "", story))))).strip()
    
    final_response["final_story_title"] = story_title
    final_response["addon_text"] = input_params.get("story_addons")

    return final_response


def rules_keys_cleaner(k):
    if isinstance(k, str):
        return regex.sub(r"extension", "extensión", regex.sub(r"genero", "género", regex.sub(r"(?<=(env|pa))i(?=o|s)", "í", regex.sub(r"_", " ", k)))).capitalize()
    else:
        return k
    
    
    

@app.route("/", methods=['GET', 'POST'])
def index():
    
    if request.method == 'GET':  
        content = {}
        content["text1"] = "Necesito que enumeres lo que consideres que podría afectar tus posibilidades de poder participar en un concurso literario" 
        content["text2"] = "(nacionalidad, lugar de residencia, edad, y, en caso de que sea aplicable, centro de estudios en el que estás matriculado):"
        session["user"] = str(uuid.uuid4())
        return render_template('index.html', content=content)
    
    else:
        if request.form.get('joining_form'):
            restricting_cond0 = regex.sub(r"^\W*|\W*$", "", request.form.get('joining_form'))+"."
            session["restriction_cond"] = restricting_cond0[0].upper()+restricting_cond0[1:]
        # elif not "restriction_cond" in session:
        else:
            session["restriction_cond"] = "Soy española, mayor de edad y hace tiempo que acabé de cursar todos mis estudios."
        return redirect(url_for("contests_rules_displayer"))


@app.route("/concursos", methods=['GET', 'POST'])
def contests_rules_displayer():
    story_addons_df0 = _read_file(story_addons_path).reset_index()
    story_addons_df = story_addons_df0.head(10)
    story_addons = dict(zip(story_addons_df.idx, story_addons_df.story_addons))
    
    if request.method == 'GET': 
        if not "accepted_contests" in session:
            accepted_contests = chatgpt_restrict_checker(contest.final_bases, session["restriction_cond"])
            session["accepted_contests"] = accepted_contests
        
        content = {}
        for k, v in contest.final_bases.items():
            if k in session["accepted_contests"]:
                content[k] = {}
                content[k]["clean_name"] = {}
                content[k]["rules"] = {}
                for ik, iv in v.items():
                    if not regex.match("(clean_name|date|nombre)$", ik):
                        content[k]["rules"][rules_keys_cleaner(ik)] = iv
                    elif regex.match("clean_name$", ik):
                        content[k]["clean_name"] = iv 
                        
        return render_template('concursos.html', content=content, story_addons=story_addons.values())
        
    else:
        session["selected_contest"] = request.form.get('select_contest_form')
        story_addons_text = regex.sub(r"^\W*|\W*$", "", request.form.get('story_addons_form'))+"."
        if len(story_addons_text) > 2:
            story_addons_idx = [k for k, v in story_addons.items() if SequenceMatcher(None, unidecode(story_addons_text), unidecode(v)).ratio() > .88]
            
            if story_addons_idx and story_addons_idx[0]:
                session["story_addons"] = story_addons_idx[0]
            else:
                story_idx1 = len(story_addons) + 1
                session["story_addons"] = story_idx1
                story_addons[story_idx1] = story_addons_text
                story_addons_df1 = pd.DataFrame(story_addons.values(), index=story_addons.keys(), columns=["story_addons"]).reset_index().rename(columns={"index":"idx"})
                _write_file(story_addons_df1, story_addons_path)

        else:
            session["story_addons"] = 0

        return redirect(url_for("story_displayer"))

  
@app.route("/cuento", methods=['GET', 'POST'])
def story_displayer():
    
    if request.method == 'GET': 
        story_addons_df = _read_file(story_addons_path).reset_index()
        story_addons = dict(zip(story_addons_df.idx, story_addons_df.story_addons))
        
        input_params, content = {}, {}

        selected_contest = session["selected_contest"]
        input_params["story_addons"] = regex.sub(r"\.+$", "", 
                                                 story_addons.get(session["story_addons"], "ostentara cierto sarcasmo."))
        input_params["bases"] = contest.final_bases.get(int(selected_contest))
        
        sc_path = os.path.join(root_path, "data", "stories", f"{selected_contest}.pkl")
        if not os.path.exists(sc_path):
            outp_dict = {}
            final_response = generate_chatgpt_story(input_params)
            outp_dict[session["story_addons"]] = final_response
            _write_file(outp_dict, sc_path)
        else:
            outp_dict = _read_file(sc_path)
            if not session["story_addons"] in outp_dict:
                final_response = generate_chatgpt_story(input_params)
                outp_dict[session["story_addons"]] = final_response
                _write_file(outp_dict, sc_path)
            else:
                final_response = outp_dict[session["story_addons"]]
        
        content["title"] = final_response.get("final_story_title")
        content["story"] = regex.sub(r"\n", "<br>", final_response.get("final_story"))
        content["bases"] = {regex.sub(r"[Cc]lean\s[Nn]ame", "Nombre", rules_keys_cleaner(k)): v for k, v in input_params["bases"].items()}

    else:
        content = {}
        content["title"] = request.form.get('downl_title_form')
        content["story"] = request.form.get('downl_story_form')
        content["bases"] = {"hello": "tu madre."}
        
    return render_template('cuento.html', content=content)

  
    
  

if __name__ == '__main__':
    app.run(debug = True, threaded = False)#, host="0.0.0.0")
    