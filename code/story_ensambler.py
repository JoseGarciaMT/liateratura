#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 19:44:39 2021

@author: jose
"""
import uuid

import requests
from bs4 import BeautifulSoup as bs
import os, regex
import random
from lxml.html import fromstring
from unidecode import unidecode
import time
from ChatGPT import ChatGPT
from tqdm import tqdm
from pprint import pprint
from datetime import datetime as dt


from DatabaseConnector import _read_file, _write_file
from Contest import Contest



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
    


if __name__ == "__main__":
    
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

    chatGPT = ChatGPT()
    contest = Contest(root_path)
    restriction_cond = "Soy una madrileña de 36 años que vive en Valencia."

    contest.get_ruled_contests()
    
    n_contests = 3
    n = 0
    accepted_contests = []
    for k, input_params in contest.final_bases.items(): 
        query_params = {}
        query_params["bases"] = input_params
        cond_sending_add = input_params.get("direccion_de_envio") and regex.search(r"\@", input_params.get("direccion_de_envio"))
        date_date = dt.strptime(input_params.get("date"), '%d:%m:%Y').date()
        fecha_date = dt.strptime(regex.sub(r"[\-\/]", ":", input_params.get("fecha_de_vencimiento")), '%d:%m:%Y').date()
        final_date = max(fecha_date, date_date)
        cond_date = dt.now().date() < final_date
        if cond_sending_add and cond_date:
            query_params["restricting_cond"] = restriction_cond
            # chatgpt_restrictions = chatGPT.query_blank_slate(prompts.get("concurso_permitido").format(**query_params), model="gpt-4o-mini")
            # cond0 = regex.search(r"(^No|(desafortunada|lamentable|desgraciada)mente|por\sdesgracia|no\scumpl((ir)?ías|[ae]s?))", chatgpt_restrictions, regex.I)
            if not False:
                accepted_contests.append(k)
                if n >= n_contests-1:
                    break
                n += 1
        
    content = {k: v for k, v in contest.final_bases.items() if k in accepted_contests}

    # pprint(content)
        
    # story = Story()
        
    print("\nQuerying ChatGPT for the story...\n")
    story_addons1 = story_addons.get(random.choice(range(1, len(story_addons)+1)))
    verbose = True    

    selected_contest = random.choice(list(content.keys()))
    input_params = {}
    input_params["bases"] = content.get(selected_contest)
    input_params["story_addons"] = story_addons1

    final_response = generate_chatgpt_story(input_params)
    
    print("\n", final_response.get("story_addons"), "\n\n")
    print("\n", final_response.get("bases").get("extension"), "\n\n")
    print("\n", final_response.get("bases").get("tema"), "\n\n")
    print("\n", final_response.get("final_story_title"), "\n")
    print("\n", final_response.get("final_story"), "\n\n")
    

    # # if input_params.get("bases")
    # # story = final_response.get("final_story")
    # extension = final_response.get("bases").get("extension", final_response.get("bases").get("extensión"))
    # all_nums = regex.findall(r"(\d+([\.\,]\d+)?)", extension)
    # all_nums1 = [int(regex.sub(r"\W", "", e[0])) for e in all_nums]
    # ext_type = regex.findall(r"(palabras|p\wginas?|folios?|l\wneas|versos|caracteres)", extension)
    # final_extension = list(zip(all_nums1, ext_type))
    
        
        

