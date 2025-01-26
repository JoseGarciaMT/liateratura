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
from datetime import datetime

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
    
    contest = Contest(root_path)
    contest.get_ruled_contests()
    
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
  


if __name__ == '__main__':
    app.run(debug = True, threaded = False)#, host="0.0.0.0")
    