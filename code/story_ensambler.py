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

    results_dict["tipo_letra"] = regex.sub(r"(?<=Times)$", " New Roman", 
                                           regex.sub(r"(?<=[tT]ime)(\s[nN]ew\s[rR]oman)?$", "s New Roman",type_letra_match.group().strip())) if type_letra_match else "Arial"
    results_dict["size_letra"] = size_letra_match.group().strip() if size_letra_match else "11"
    inter_letra0 = (interlineado_match.group().strip() if interlineado_match else ("2" if interlineado_match1 else "1.15"))

    results_dict["inter_letra"] = regex.sub(r"\,", ".", inter_letra0)
    return results_dict



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
    
    
    # accepted_contests = chatgpt_restrict_checker(contest.final_bases, restriction_cond, n_contests=5)

    # content = {k: {"bases": v} for k, v in contest.final_bases.items() if k in accepted_contests}

    # pprint(content)
        
    format_dict = {}
    for key, input_params in contest.final_bases.items():
        ruled_format = input_params.get("formato")
        format_dict[key] = format_cleaner(ruled_format)
        format_dict[key]["whole_format"] = ruled_format
    pprint(format_dict)

    # assert 0 == 1
    # print("\nQuerying ChatGPT for the story...\n")
    # story_addons1 = story_addons.get(random.choice(range(1, len(story_addons)+1)))
    # verbose = True    

    # selected_contest = random.choice(list(content.keys()))
    # input_params = {}
    # input_params["bases"] = content.get(selected_contest)
    # input_params["story_addons"] = story_addons1
              
    # final_response = generate_chatgpt_story(input_params, )
    
    # print("\n", final_response.get("story_addons"), "\n\n")
    # print("\n", final_response.get("final_story_title"), "\n")
    # print("\n", final_response.get("final_story"), "\n\n")
    

    # # if input_params.get("bases")
    # # story = final_response.get("final_story")
    # extension = final_response.get("bases").get("extension", final_response.get("bases").get("extensión"))
    # all_nums = regex.findall(r"(\d+([\.\,]\d+)?)", extension)
    # all_nums1 = [int(regex.sub(r"\W", "", e[0])) for e in all_nums]
    # ext_type = regex.findall(r"(palabras|p\wginas?|folios?|l\wneas|versos|caracteres)", extension)
    # final_extension = list(zip(all_nums1, ext_type))

        

