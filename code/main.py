#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 09:26:05 2019

@author: rita

Flask app

"""

import regex, os
import pandas as pd

from unidecode import unidecode

from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory

import uuid
import datetime
from dateutil import parser
from difflib import SequenceMatcher

from DatabaseConnector import _write_file, _read_file, _path_exists
from GDriveManager import GDriveManager
from Contest import Contest
from ChatGPT import ChatGPT


app = Flask(__name__)
app.secret_key = b'_asgagasgas@$'

## PATHS
root_path = os.path.dirname(os.path.dirname(__file__))
data_path = os.path.join(root_path, "data", "available_contests0.csv")
prompts_path = os.path.join(root_path, "data", "utils", "prompts.csv")
story_addons_path = os.path.join(root_path, "data", "utils", "story_addons.csv")
naked_bases_path = os.path.join(root_path, "data", "naked_bases.pkl")
bases_path = os.path.join(root_path, "data", "users", "all_rules.pkl")
accepted_contests_path = os.path.join(root_path, "data", "users", "user_rules.pkl")
downloads_path = os.path.join(root_path, "data", "tmp")


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
        cond_sending_add = input_params.get("direccion_de_envio") and regex.search(r"(\@|https:\/\/)", input_params.get("direccion_de_envio"))
        if input_params.get("fecha_de_vencimiento"):
            if isinstance(input_params.get("fecha_de_vencimiento"), datetime.date):
                back2dt = input_params.get("fecha_de_vencimiento")
            elif isinstance(input_params.get("fecha_de_vencimiento"), str) and regex.search(r"(\:\d+){2}", input_params.get("fecha_de_vencimiento")):
                back2dt = datetime.datetime.strptime(input_params.get("fecha_de_vencimiento"), "%d:%m:%Y").date()
            else:
                back2dt = datetime.date.today() - datetime.timedelta(days=1)

        cond_date = datetime.date.today() < back2dt
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
    cond_title1 = regex.search(r"^\W*([A-Z]\w+([^\n\w\-\#\*]{1,3}\w+){,25}[^\n\w\-\#\*]*)(?=\W*\n+[A-Z][a-záéíóú]+\s([A-Z][a-záéíóú]+){,3}[a-záéíóú]{2,})", story)

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
    

def format_cleaner(ruled_format, letter_type_list=[
        "([Ss]ans\-)?[Ss]erif", "Helvetica", "Arial", "Times?", 
        "Futura", "Garamond", "Roboto", "Calibri", 
        "Verdana", "Lucida", "Courier", "Cambria", "(Open\-)?sans"
        ]):
    
    letter_type_str = "(?<=(^|\W))(({})(\s[A-Z]\w+)*)(?=($|\W))".format("|".join(letter_type_list))

    results_dict = {}

    type_letra_match0 = regex.search(regex.compile(letter_type_str), ruled_format)
    type_letra_match1 = regex.search(r"(?<=(^|\s)([lL]etra|[Tt]ipo|[fF]uente)\s)([A-Z]\w+\s?){1,4}", ruled_format)
    type_letra_match = type_letra_match1 if type_letra_match1 else type_letra_match0
    
    if type_letra_match:
        letter_type_str = regex.escape(type_letra_match.group().strip())
        
    letter_size_str = "(?<=tama\wo\s(\w+\s){,3})1\d(?=(\D|$))|(?<=([lL]etra|[Tt]ipo|[fF]uente)\s(\W?\w+\W+){1,5})1\d(?=\s?(puntos|pts?))"+f"|(?<={letter_type_str}\W(\w+\,?\s)*)(1\d)(?=(\D|$))"
    size_letra_match = regex.search(regex.compile(letter_size_str), ruled_format)
    
    interlineado_match = regex.search(r"(?<=(espaci(ad)?o|interlineado)\s(\w+\s){,3})(\d([\,\.]\d{1,2})?)|(\d([\,\.]\d{1,2})?)(?=\s(\w+\s){,2}(espaci(ad)?o|interlineado))", ruled_format, regex.I)
    interlineado_match1 = regex.search(r"\b(doble|interlineado|espacio)\s(doble|interlineado|espacio)\b", ruled_format, regex.I)

    results_dict["font_family"] = regex.sub(r"(?<=Times)$", " New Roman", 
                                           regex.sub(r"(?<=[tT]ime)(\s[nN]ew\s[rR]oman)?$", "s New Roman",type_letra_match.group().strip())) if type_letra_match else "Arial"
    results_dict["font_size"] = size_letra_match.group().strip() if size_letra_match else "11"
    inter_letra0 = (interlineado_match.group().strip() if interlineado_match else ("2" if interlineado_match1 else "1.15"))

    results_dict["line-height"] = regex.sub(r"\,", ".", inter_letra0)
    return results_dict



@app.route("/", methods=['GET', 'POST'])
def index():
    
    session['todays_visit'] = datetime.date.today() #+ datetime.timedelta(days=7)
    if not "user" in session:
        session['user'] = str(uuid.uuid4())
        session['last_visit'] = datetime.date.today()

    if isinstance(session["last_visit"], str):
        last_visit = parser.parse(session["last_visit"]).date()
    else:
        last_visit = session["last_visit"]
        
    difference = session['todays_visit'] - last_visit
    time_lapse = datetime.timedelta(days=7)
    
    if not "restriction_cond" in session or difference >= time_lapse:
        if request.method == 'GET':  
            content = {}
            content["text1"] = "Necesito que enumeres lo que consideres que podría mermar tus posibilidades de ser aceptado para entrar a participar en un certamen literario" 
            content["text2"] = "(nacionalidad, lugar de residencia, edad, y, en caso de que sea aplicable, centro de estudios en el que estás matriculado):"
            return render_template('index.html', content=content)
        else:
            restricting_cond0 = regex.sub(r"^\W*|[\.\,\;\:\s\n]*$", "", request.form.get('joining_form'))+"."
            session["restriction_cond"] = restricting_cond0[0].upper()+restricting_cond0[1:]
            session["last_visit"] = session['todays_visit']
            return redirect(url_for("contests_rules_displayer"))
    else:
        return redirect(url_for("contests_rules_displayer"))



@app.route("/concursos", methods=['GET', 'POST'])
def contests_rules_displayer():
    story_addons_df0 = _read_file(story_addons_path).reset_index()
    story_addons_df = story_addons_df0.head(10)
    story_addons = dict(zip(story_addons_df.idx, story_addons_df.story_addons))
    
    if request.method == 'GET': 
        # print("\n"+session.get("last_visit", "whats up?")+"\n", file=sys.stderr)
        if isinstance(session["last_visit"], str):
            last_visit = parser.parse(session["last_visit"]).date()
        else:
            last_visit = session["last_visit"]
            
        if isinstance(session["todays_visit"], str):
            todays_visit = parser.parse(session["todays_visit"]).date()
        else:
            todays_visit = session["todays_visit"]
            
        difference = todays_visit - last_visit
        time_lapse = datetime.timedelta(days=1)
        if not "accepted_contests" in session or difference >= time_lapse:
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
    
    selected_contest = session["selected_contest"]

    input_params = {}
    input_params["bases"] = contest.final_bases.get(int(selected_contest))
    if request.method == 'GET': 
        story_addons_df = _read_file(story_addons_path).reset_index()
        story_addons = dict(zip(story_addons_df.idx, story_addons_df.story_addons))
    
        input_params["story_addons"] = regex.sub(r"\.+$", "", 
                                                 story_addons.get(session["story_addons"], "ostentara cierto sarcasmo."))

        content = {}
        
        sc_path = os.path.join(root_path, "data", "stories", f"{selected_contest}.pkl")
        if not _path_exists(sc_path):
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

        return render_template('cuento.html', content=content)
    
    else:
        title = request.form.get('downl_title_form')
        story = request.form.get('downl_story_form')
        
        ruled_format = input_params.get("bases").get("formato")
        
        format_dict = format_cleaner(ruled_format)
        
        title = title.strip()
        
        gdriver = GDriveManager()
        mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        
        filename = title + ".docx"
        
        file_id = gdriver.generate_gdoc_from_text(title, story, title, format_dict)
        
        filestream = gdriver.get_fstream_from_gdoc(gdoc_id = file_id, 
                                                     mimeType = mime)
        
        tmp_files = [ f for f in os.listdir("/tmp") if f.endswith(".docx") ]
        for fname in tmp_files:
            os.remove(os.path.join("/tmp",fname))

        with open(os.path.join("/tmp",filename),"wb") as f:
            f.write(filestream)
            
        return send_from_directory("/tmp", filename, as_attachment=True)

@app.route("/update_contests",  methods=['POST'])
def new_contests_loader():
    contest.downloading_contest_info()
    _write_file(contest.naked_bases, contest.naked_bases_path)
    return "Success", 201
        
    

if __name__ == '__main__':
    app.run(debug = True, threaded = False)#, host="0.0.0.0")
    