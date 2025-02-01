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
import datetime


from DatabaseConnector import _read_file, _write_file
from Contest import Contest
from main import generate_chatgpt_story, chatgpt_restrict_checker, rules_keys_cleaner





if __name__ == "__main__":
    
    ## PATHS
    root_path = os.path.dirname(os.path.dirname(__file__))
    # root_path = os.path.dirname(os.getcwd())

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
    print(contest.final_bases.get(1).keys())
    
    
    accepted_contests = chatgpt_restrict_checker(contest.final_bases, restriction_cond, n_contests=5)

    content = {k: v for k, v in contest.final_bases.items() if k in accepted_contests}

    pprint(content)
                
    assert 0 == 1
    print("\nQuerying ChatGPT for the story...\n")
    story_addons1 = story_addons.get(random.choice(range(1, len(story_addons)+1)))
    verbose = True    

    selected_contest = random.choice(list(content.keys()))
    input_params = {}
    input_params["bases"] = content.get(selected_contest)
    input_params["story_addons"] = story_addons1
              
    final_response = generate_chatgpt_story(input_params, )
    
    print("\n", final_response.get("story_addons"), "\n\n")
    print("\n", final_response.get("final_story_title"), "\n")
    print("\n", final_response.get("final_story"), "\n\n")
    

    # # if input_params.get("bases")
    # # story = final_response.get("final_story")
    # extension = final_response.get("bases").get("extension", final_response.get("bases").get("extensión"))
    # all_nums = regex.findall(r"(\d+([\.\,]\d+)?)", extension)
    # all_nums1 = [int(regex.sub(r"\W", "", e[0])) for e in all_nums]
    # ext_type = regex.findall(r"(palabras|p\wginas?|folios?|l\wneas|versos|caracteres)", extension)
    # final_extension = list(zip(all_nums1, ext_type))

        

