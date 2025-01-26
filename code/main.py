#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 09:26:05 2019

@author: rita

Flask app

"""

import regex, os, io
from random import sample
import pandas as pd
import numpy as np 

from unidecode import unidecode

from flask import Flask, render_template, request, session, redirect, url_for, flash

import uuid
import time
from datetime import datetime as dt

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

story_addons_df = _read_file(story_addons_path).reset_index()
story_addons = dict(zip(story_addons_df.idx, story_addons_df.story_addons))

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


def generate_chatgpt_story(input_params):

    story = chatGPT.query_blank_slate(prompts.get("extraer_cuento").format(**input_params), model="gpt-4o-mini")
              
    cond1 = len(regex.findall(r"(\*{2,}[A-Z]\w*(\s\w+){,2}\:?\*{2,})|(\#+\s?[A-Z]\w+\:)", story)) <= 3
    cond2 = len(regex.findall(r"[\#\*]{2,}\s?(sinopsis|introducci\wn|desenlace|conclusi\wn|estructura|desarrollo|cl\wmax)", story, regex.I)) <= 2
    cond3 = len(regex.findall(r"[\#\*]{2,}\s?(parte|cap\wtulo|[ivx]+)\s?\d+", story, regex.I)) <= 3
    
    if not (cond1 and cond2 and cond3):
        story = chatGPT.query_blank_slate(prompts.get("extraer_cuento").format(**input_params), model="gpt-4o-mini")
        
    final_comments_re = r"\n\s*(\-{3,}|\W{2,}Fin((al)?\sdel\s([Aa]cto|[cC]uento|[rR]elato))?\W{2,})\s*\n(\W?[\w\s\:\,\:]+[\?\!\.]){1,3}$"
    final_comments_re1 = r'[\-\#\*]+([lL]as\s)?[fF]rases\s[hH]echas(.|\n){10,800}$'
    rex_cleaner = regex.compile("(^\W*(((Claro|Por\ssupuesto|A\scontinuación)\,\s)?(aquí\stienes|puedo\s\w+|te\spresento\s\w+)[^\.]+)?(t\wtulo)?\W+|[\n\s]+$)", regex.I)

    story_title = regex.sub(r"(^\W+|\W+$)", "", regex.search(r"(?<=^\W*(t\wtulo|\w+\:)\W+)[^\n]+", story, regex.I).group()) if regex.search(r"(?<=^\W*(t\wtulo|\w+\:)\W+)[^\n]+", story, regex.I) else ""
    input_params["final_story"] = regex.sub(r"^\W+", "", regex.sub(rex_cleaner, "", 
                                            regex.sub(regex.compile(regex.escape(story_title)), "", 
                                                      regex.sub(r"(?<=\W)[\#\*]+Fin\W*$", "", 
                                                                regex.sub(final_comments_re1, "", 
                                                                          regex.sub(final_comments_re, "", story)))))).strip()
    
    input_params["final_story_title"] = story_title

    return input_params



@app.route("/", methods=['GET', 'POST'])
def index():
    
    if request.method == 'GET':  
        content = {}
        content["text"] = "Necesito que enumeres lo que consideres que podría afectar tus posibilidades de poder participar en un concurso de relatos."
        return render_template('index.html', content=content)
    
    else:
        session["restriction_cond"] = request.form.get('joining_form')
        return redirect(url_for("contests_rules_displayer"))



@app.route("/concursos", methods=['GET', 'POST'])
def contests_rules_displayer():
    
    if request.method == 'GET': 
        if not "accepted_contests" in session:
            restriction_cond = session["restriction_cond"]
            n_contests = 9
            n = 0
            accepted_contests = []
            for k, input_params in contest.final_bases.items(): 
                query_params = {}
                query_params["bases"] = input_params
                if input_params.get("direccion_de_envio") and regex.search(r"\@", input_params.get("direccion_de_envio")):
                    query_params["restricting_cond"] = restriction_cond
                    cond_sending_add = input_params.get("direccion_de_envio") and regex.search(r"\@", input_params.get("direccion_de_envio"))
                    date_date = dt.strptime(input_params.get("date"), '%d:%m:%Y').date()
                    fecha_date = dt.strptime(regex.sub(r"[\-\/]", ":", input_params.get("fecha_de_vencimiento")), '%d:%m:%Y').date()
                    final_date = max(fecha_date, date_date)
                    cond_date = dt.now().date() < final_date
                    if cond_sending_add and cond_date:
                        chatgpt_restrictions = chatGPT.query_blank_slate(prompts.get("concurso_permitido").format(**query_params), model="gpt-4o-mini")
                        cond0 = regex.search(r"(^No|(desafortunada|lamentable|desgraciada)mente|por\sdesgracia|no\scumpl((ir)?ías|[ae]s?))", chatgpt_restrictions, regex.I)
                        if not cond0:
                            accepted_contests.append(k)
                            if n >= n_contests-1:
                                break
                            n += 1
                        
            session["accepted_contests"] = accepted_contests
    
        content = {k: v for k, v in contest.final_bases.items() if k in session["accepted_contests"]}
        return render_template('concursos.html', content=content)
        
    else:
        session["selected_contest"] = request.form.get('select_contest_form')
        session["story_addons"] = request.form.get('story_addons_form')
        return redirect(url_for("story_displayer"))

  
    
@app.route("/cuento", methods=['GET', 'POST'])
def story_displayer():
    
    if request.method == 'GET': 
        
        input_params, content = {}, {}

                          
    return render_template('cuento.html', content=content)
  
    
  

if __name__ == '__main__':
    app.run(debug = True, threaded = False)#, host="0.0.0.0")
    