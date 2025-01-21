#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 19:44:39 2021

@author: jose
"""

import urllib
import requests
from bs4 import BeautifulSoup as bs
import os, regex
import random
import pandas as pd
from collections import Counter
from lxml.html import fromstring
from unidecode import unidecode
import time
from ChatGPT import ChatGPT
from pprint import pprint
from tqdm import tqdm



def get_proxies(url):
       """
       Function meant to provide different proxies 
       to scrape the website of the url provided as input.
       """
       
       try:
           r_obj = requests.get(url)
       except:
           proxy = 0
           while not type(proxy) == str:
               try:
                   url = 'https://free-proxy-list.net/'
                   response = requests.get(url)
                   parser = fromstring(response.text)
                   ip = random.choice(parser.xpath('//tbody/tr'))
                   if ip.xpath('.//td[7][contains(text(),"yes")]'):
                       proxy = ":".join([ip.xpath('.//td[1]/text()')[0], ip.xpath('.//td[2]/text()')[0]])
                       proxies = {"http": proxy, "https": proxy}
                       
               except:
                  continue
      
           r_obj = requests.get(url, proxies)
                  
       return r_obj
  
    
def _get_proxies(url, raw_prox=[]):
      """
      Function meant to provide different proxies 
      to scrape the website of the url provided as input.
      """
      if not raw_prox:
          fix_url = 'https://free-proxy-list.net/'
          response = requests.get(fix_url)
          core_soup = bs(response.text, "html.parser")
          ips = [regex.sub(r"[\<td\>\/]", "", str(e)) for e in core_soup.find_all("td") if regex.match(r"\<td\>\d+(\.\d+){3}\<", str(e))]
          ports = [regex.sub(r"[\<td\>\/]", "", str(e)) for e in core_soup.find_all("td") if regex.match(r"\<td\>\d+\<", str(e))]
          raw_prox = [":".join(e) for e in list(zip(ips, ports))]
      
      proxy = random.choice(raw_prox)
      proxies = {"http"  : "http://" + proxy, 
                 "https" : "http://" + proxy, 
                 "ftp"   : "http://" + proxy} 
      
      r_obj = ""
      i = 0
      while i <= 1000 and not r_obj:
          i += 1
          try:
              r_obj = requests.get(url, proxies).text
          except:
              proxy = random.choice(raw_prox)
              proxies = {"http"  : "http://" + proxy, 
                         "https" : "http://" + proxy, 
                         "ftp"   : "http://" + proxy}
      return r_obj


def relevant_info_retriever(mini_soup, raw0):
    
    concursos_dict_n = {}
    content_end = regex.search(r"BASES[IVX\W\:]*", raw0).start()
    raw = raw0[:content_end]
    gender = regex.findall(r"(?<=Género\:\s*)[\w\s\,\;\.+]+(?=Premio\:)", raw)[0].strip()
    price = regex.findall(r"(?<=Premio\:\s*).+(?=Abierto\sa\:)", raw)[0].strip()
    restrictions = regex.findall(r"(?<=Abierto\sa\:\W*)\w[\W\w]+(?=Entidad\sconvocante\:)", raw)[0].strip()
    entity = regex.findall(r"(?<=Entidad\sconvocante\:\W*)\w[\W\w]+(?=País\sde\sla\sentidad\sconvocante\:)", raw)[0].strip()
    country = regex.findall(r"(?<=País\sde\sla\sentidad\sconvocante\:\W*)([A-Z]\w[\W\w]+)(?=Participación\spor\smedios\selectrónicos\:)|(?=Fecha\sde\scierre\:)", raw)[0].strip()
    via_mail0 = regex.findall(r"(?<=Participación\spor\smedios\selectrónicos\:\W*)([sS]í|[nN]o)(?=Fecha\sde\scierre\:)", raw)
    via_mail = via_mail0[0].strip() if via_mail0 else "N/A"
    expiration_date = regex.findall(r"(?<=Fecha\sde\scierre\:\W*)((\d+\:){2}\d+)", raw)[0][0].strip()

    raw1 = ". ".join([div.text for div in mini_soup.find_all("p") if div.text and not div.text == '\xa0'])
    content_start = regex.search(r"\.\s+BASES[IVX\:]*\.", raw1).end()
    content_end = regex.search(r"©", raw1).start()
    raw2 = raw1[content_start:content_end]
    sending_address0 = regex.findall(r"(?<=href\=\Wmailto\:)\S+(?=\W\>)", str(mini_soup)) if not regex.search(r"No", via_mail) else None
    sending_address = sending_address0[0] if sending_address0 else None

    leng_alter, formato, extension, tema = '', '', '', ''
    parr_num_re = r"((?<=\.+\s*)((Primer|Segund|Tercer|Cuart|Quint|Sext|Sép?tim|Octav|Noven|(Un|Duo)?[Dd]écim)\w*|\d{1,2}[ºª°][\.\:\-]+|\•)[^\.]*)"
    if regex.search(parr_num_re, raw2, regex.I):
        clausulas = [e[0] for e in regex.findall(parr_num_re, raw2, regex.I) if e and len(e) > 3]
        raw3 = raw2
        for i, clau in enumerate(clausulas):
            prev_clau_i = regex.search(regex.compile(clausulas[i-1]), raw3).end() if i>0 else 0
            clau1 = raw3[prev_clau_i:regex.search(regex.compile(clau), raw3).start()]
            if regex.search(r"\b(tem[áa]\w*(?!\sdel\smensaje)|trat(e|ar)\s(sobre|acerca)|reflej|vers(e|ar))\b", clau1, regex.I):
                tema = regex.sub(r"^\W+", "", clau1)
            if regex.findall(r"\b(palabras|folio|líneas|caracteres|extensi[oó]n|longitud)\b", clau1, regex.I):
                extension = clau1
            if regex.findall(r"\b(formato|tamaño|letra|interlineado|arial|times\s\new\s\roman)\b", clau1, regex.I):
                formato = clau1
            if regex.findall(r"\b(catalán|eusquera|aragonés|gallego|lenguas\s(co?\-?)?oficiales)\b", clau1, regex.I):
                leng_alter = clau1
            raw3 = raw2[prev_clau_i:]
    else:
        tema0 = regex.search(r"([^\.]*\W(tem[áa]\w*(?!\sdel\smensaje)|trat(e|ar)\s(sobre|acerca)|reflej|vers(e|ar))[^\.]*)", raw2, regex.I)
        tema = tema0[0][0] if tema0 else "N/A"
        extension0 = regex.findall(r"([^\.]*\W(palabras|folio|líneas|caracteres|extensi[oó]n|longitud)[^\.]*)", raw2, regex.I)
        extension = extension0[0][0] if extension0 else "N/A"
        formato0 = regex.findall(r"([^\.]*\W(formato|tamaño|letra|interlineado|arial|times\s\new\s\roman)[^\.]*)", raw2, regex.I)
        formato = formato0[0][0] if formato0 else "N/A"
        leng_alter0 = regex.findall(r"([^\.]*\W(catalán|eusquera|aragonés|valenciano|gallego|lenguas\s(co?\-?)?oficiales)[^\.]*)", raw2, regex.I)
        leng_alter = leng_alter0[0][0] if leng_alter0 else "N/A"

    concursos_dict_n["nombre"] = name
    concursos_dict_n["fecha de vencimiento"] = expiration_date
    concursos_dict_n["link"] = url
    concursos_dict_n["envío por email"] = via_mail
    concursos_dict_n["país convocante"] = country
    concursos_dict_n["entidad convocante"] = entity
    concursos_dict_n["restricciones"] = restrictions
    concursos_dict_n["premio"] = price
    concursos_dict_n["género"] = gender
    concursos_dict_n["tema"] = tema
    concursos_dict_n["extensión"] = extension
    concursos_dict_n["dirección de envío"] = sending_address
    concursos_dict_n["formato"] = formato
    concursos_dict_n["otros idiomas"] = leng_alter

    
    return concursos_dict_n



def contest_site_querier(url = "https://www.escritores.org/concursos/concursos-1/concursos-cuento-relato"):

    resp = get_proxies(url)
    
    soup = bs(resp.content, "html.parser")
        
    content = soup.find(id="cuento") 

    return content

    


if __name__ == "__main__":
    
    ## PATHS
    root_path = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(root_path, "data", "available_contests0.csv")
    finaldata_path = os.path.join(root_path, "data", "available_contests.csv")
    prompts_path = os.path.join(root_path, "data", "prompts.csv")
    
    if os.path.exists(finaldata_path):
        whole_df = pd.read_csv(finaldata_path)
    else:
        prompts_df = pd.read_csv(prompts_path)
        prompts = dict(zip(prompts_df.tipo, prompts_df.prompt))
        
        ## VARS
        url = "https://www.escritores.org/concursos/concursos-1/concursos-cuento-relato"
        chatGPT = ChatGPT()
        input_params = {}

        input_params["restricting_cond"] = "Soy una madrileña de 36 años que vive en Valencia."
        input_params["story_addons"] = "importe que uno de sus personajes sea un funcionario que haya muerto por el ejercicio de su labor."
        
        concursos_dict = {}
        dfs = []
        n = 0
        
        content = contest_site_querier(url)
        
        for mes in content.find_all("ul"):
            for concurso in tqdm(mes.find_all("li")):
                n += 1
        
                name, expiration_date, url, via_mail, country, entity, restrictions, price, gender, tema, extension, sending_address, formating = "", "", "", "", "", "", "", "", "", "", "", "", ""
                concursos_dict_n = {}
                name = regex.sub(r"(?<=\)).*", "", concurso.find("span").text)
                date = regex.search(r"\d{2}:\d{2}:\d{4}", concurso.text).group()
                cond_mail = concurso.find("img")
                cond_spain = regex.search(r"España", concurso.text)
                cond_age = regex.search(r"Abierto\sa\:\s(\w+\,?\s)*((menores\sde|y)\s([123]\d|diec|veint|treint)|(mayores\sde)\s([4567]\d|cuarent|cincuenta|se[ts]enta))|(nacidos?\sentre\s(\w+\s)*\d\.?\d+(\-|\sy\s)\d\.?\d+)", concurso.text)
                cond_resid = regex.search(r"Abierto\sa\:\s(\w+\,?\s)*(municipio|provincia|[Cc]omunidad\s[Aa]ut|ciudad|empadronad)", concurso.text)
                cond_alumn = regex.search(r"Abierto\sa\:\s(\w+\,?\s)*(alumno|estudiante|matriculad)", concurso.text)
                
                concursos_dict_n["x_mail"] = bool(cond_mail)
                concursos_dict_n["from_spain"] = bool(cond_spain)
                concursos_dict_n["age_restriction"] = bool(cond_age)
                concursos_dict_n["residency_restriction"] = bool(cond_resid)
                concursos_dict_n["student_restriction"] = bool(cond_alumn)
                
                
                if cond_mail and cond_spain and not (cond_age or cond_resid or cond_alumn):
                    url = "https://www.escritores.org"+concurso.find("a")["href"]
                    resp0 = get_proxies(url)
                    if not resp0:
                        time.sleep(1)
                        resp0 = get_proxies(url)
            
                    if resp0:
                        mini_soup = bs(resp0.content, "html.parser")
                        # Cleaning string
                        input_params["raw"] = mini_soup.getText()
                        input_params["regex_out"] = relevant_info_retriever(mini_soup, input_params["raw"])  
                        input_params["regex_out_keys"] = list(input_params.get("regex_out").keys())
                        
                        input_params["chatgpt_restrictions"] = chatGPT.query_blank_slate(prompts.get("concurso_permitido").format(**input_params))
                                          
                        if not regex.search(r"(^No|desafortunadamente|lamentablemente|por\sdesgracia|no\scumples)", input_params["chatgpt_restrictions"], regex.I):
                            
                            chatgpt_resp_bases = chatGPT.query_blank_slate(prompts.get("extraer_bases").format(**input_params))
                                    
                            keys = list(input_params["regex_out"].keys())
                            end_ch = 0
                            concursos_dict[n] = {}
                            for i, e in enumerate(keys):
                                end_ch = regex.search(regex.compile(keys[i+1]), chatgpt_resp_bases).start() if (i+1 < len(keys)-1 and regex.search(regex.compile(keys[i+1]), chatgpt_resp_bases)) else (end_ch + regex.search(r"\n+", chatgpt_resp_bases[end_ch:]).end() if regex.search(r"\n+", chatgpt_resp_bases[end_ch:]) else end_ch)
                                concursos_dict[n][e] = regex.sub(r"^\W+|[\,\W]+$", "", chatgpt_resp_bases[regex.search(regex.compile(e), chatgpt_resp_bases).end(): end_ch])

                            input_params["bases"] = concursos_dict[n]
                            input_params["chatgpt_resp_cuento"] = chatGPT.query_blank_slate(prompts.get("extraer_cuento").format(**input_params))
                                      
                            all_weirdos = regex.findall(r"(\*{2}[A-Z]\w*(\s\w+){,2}\:?\*{2})|(\#+\s?[A-Z]\w+\:)", input_params["chatgpt_resp_cuento"])
                                      
                            if len(all_weirdos) > 2:
                                input_params["chatgpt_resp_cuento1"] = chatGPT.query_blank_slate(prompts.get("reextraer_cuento").format(**input_params))
                            
                            input_params.update(concursos_dict_n)
                            
                            output_dict = {}
                            for k, v in input_params.items():
                                if isinstance(v, str) and k != "raw":
                                    output_dict[k] = v
                                elif isinstance(v, dict) and regex.search(r"bases|regex_out", k):
                                    for k1, v1 in v.items():
                                        output_dict[f"{k}_"+regex.sub(r"\s", "_", k1)] = v1
                            
                            final_df_dict = {}
                            ucols = [e for e in set(list(map(lambda x: regex.sub(r"^(regex_out|bases)_", "", x) if regex.search(r"^(regex_out|bases)_", x) else None, output_dict.keys()))) if e]
                            for col in ucols:
                                similar_info = [e for e in output_dict.keys() if regex.search(col, e)]
                                if similar_info:
                                    final_df_dict[col] = set([output_dict.get(similar_info[0]), output_dict.get(similar_info[1])])            
                                
                            final_df_dict.update({k: v for k, v in output_dict.itmes() if not regex.match(r"raw|regex|bases", k)})
                            dfs.append(pd.DataFrame(final_df_dict, index=[n]))
                                                        
                            if n % 15 == 0 and n > 1:
                                whole_df = pd.concat(dfs, axis=0)
                                whole_df.to_csv(data_path)
                                print("Shape of dataframe to save:", whole_df.shape)
                                print("-------------------NEXT BATCH-----------------------")
                                print()
        
        

        whole_df = pd.concat(dfs, axis=0)
        whole_df.to_csv(finaldata_path)
        print(whole_df[["nombre", "tema", "chatgpt_cond_resp", "chatgpt_output"]].head())
        
    

    
    
