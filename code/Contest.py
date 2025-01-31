#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 13 10:08:25 2024

@author: josegmt
"""

import uuid

from Story import Story
from Plica import Plica
# from EmailUtils import send_email

import requests
from bs4 import BeautifulSoup as bs
import os, regex
import random
from datetime import datetime as dt

from lxml.html import fromstring
from unidecode import unidecode
import time
from ChatGPT import ChatGPT
from tqdm import tqdm

from DatabaseConnector import _read_file, _write_file
    

class Contest:
    
    def __init__(self, root_path):
        
        self.contest_uuid = uuid.uuid4()
        self.url = "https://www.escritores.org/concursos/concursos-1/concursos-cuento-relato"
        self.root_path = root_path
        self.naked_bases_path = os.path.join(root_path, "data", "naked_bases.pkl")
        self.bases_path = os.path.join(root_path, "data", "users", "all_rules.pkl")
        self.accepted_contests_path = os.path.join(root_path, "data", "users", "user_rules.pkl")
        
        self.final_bases = None
        self.naked_bases = None
        
        prompts_path = os.path.join(root_path, "data", "utils", "prompts.csv")
        prompts_df = _read_file(prompts_path)
        self.prompts = dict(zip(prompts_df.tipo, prompts_df.prompt))

        self.chatGPT = ChatGPT()


    def _get_proxies(self, url):
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
      

    def relevant_info_retriever(self, mini_soup):
        
        raw0 = mini_soup.getText()
        
        concursos_dict_n = {}
        content_end = regex.search(r"BASES[IVX\W\:]*", raw0).start()
        
        raw = raw0[:content_end]
        name = (regex.search(r"^(([XIVL]*\.?|\d+\S*|(PRIMER|SEGUNDO|TERCER|CUARTO|QUINTO))\s)?(EDICIÓN|CONCURSO|CERTAMEN|PREMIO)\s[^\-]+(?=\W+Escritores.org\W+)", raw.strip()).group().strip() 
                if regex.search(r"^(([XIVL]*\.?|\d+\S*|(PRIMER|SEGUNDO|TERCER|CUARTO|QUINTO))\s)?(EDICIÓN|CONCURSO|CERTAMEN|PREMIO)\s[^\-]+(?=\W+Escritores.org\W+)", raw.strip()) 
                else (regex.search(r"^[^\-]+(?=\-\s*Escritores.org\W+)", raw.strip()).group().strip() 
                      if regex.search(r"^[^\-]+(?=\-\s*Escritores.org\W+)", raw.strip()) else ""))
        gender = regex.findall(r"(?<=Género\:\s*)[\w\s\,\;\.+]+(?=Premio\:)", raw)[0].strip()
        price = regex.findall(r"(?<=Premio\:\s*).+(?=Abierto\sa\:)", raw)[0].strip()
        restrictions = regex.findall(r"(?<=Abierto\sa\:\W*)\w[\W\w]+(?=Entidad\sconvocante\:)", raw)[0].strip()
        entity = regex.findall(r"(?<=Entidad\sconvocante\:\W*)\w[\W\w]+(?=País\sde\sla\sentidad\sconvocante\:)", raw)[0].strip()
        country = regex.findall(r"(?<=País\sde\sla\sentidad\sconvocante\:\W*)([A-Z]\w[\W\w]+)(?=Participación\spor\smedios\selectrónicos\:)|(?=Fecha\sde\scierre\:)", raw)[0].strip()
        via_mail0 = regex.findall(r"(?<=Participación\spor\smedios\selectrónicos\:\W*)([sS]í|[nN]o)(?=Fecha\sde\scierre\:)", raw)
        via_mail = via_mail0[0].strip() if via_mail0 else "N/A"
        expiration_date = regex.findall(r"(?<=Fecha\sde\scierre\:\W*)((\d+\W){2}\d+)", raw)[0][0].strip()
    
        raw1 = ". ".join([div.text for div in mini_soup.find_all("p") if div.text and not div.text == '\xa0'])
        content_start = regex.search(r"\.\s+BASES[IVX\:]*\.", raw1).end()
        content_end = regex.search(r"©", raw1).start()
        raw2 = raw1[content_start:content_end]
        sending_address0 = regex.findall(r"(?<=href\=\Wmailto\:)\S+(?=\W\>)", str(mini_soup)) if not regex.search(r"No", via_mail) else None
        sending_address = sending_address0[0] if sending_address0 else None
    
        leng_alter, formato, extension, tema = '', '', '', ''
        parr_num_re = r"(?<=\.+\s*)(((Primer|Segund|Tercer|Cuart|Quint|Sext|Sép?tim|Octav|Noven|(Un|Duo)?[Dd]écim)\w*|\d{1,2}[ºª°])[\.\:\-]+|\•)?([^\.]*)"
        if regex.search(parr_num_re, raw2, regex.I):
            all_parrs = regex.findall(parr_num_re, raw2, regex.I)
            clausulas = [sorted(list(e), key=len)[-1] for e in all_parrs if e and len("".join(e)) > 20]
            if clausulas:
                raw3 = raw2
                for i, clau in enumerate(clausulas):
                    prev_clau_i = (regex.search(regex.compile(regex.escape(clausulas[i-1])), raw2).end() 
                                   if i>0 and regex.search(regex.compile(regex.escape(clausulas[i-1])), raw2)
                                   else regex.search(parr_num_re, raw3).end())
                    last_char = regex.search(regex.compile(regex.escape(clau)), raw3).start() if regex.search(regex.compile(regex.escape(clau)), raw3) else len(raw3)-1
                    clau1 = raw3[prev_clau_i:last_char]
                    if regex.search(r"\b(tem[áa]\w*(?!\sdel\smensaje)|trat(e|ar)\s(sobre|acerca)|reflej|vers(e|ar))\b", clau1, regex.I):
                        tema = regex.sub(r"^\W+", "", clau1)
                    if regex.search(r"\b(palabras|folio|líneas|caracteres|extensi[oó]n|longitud)\b", clau1, regex.I):
                        extension = clau1
                    if regex.search(r"\b(formato|tamaño|letra|interlineado|arial|times\s\new\s\roman)\b", clau1, regex.I):
                        formato = clau1
                    if regex.search(r"\b(catalán|eusquera|aragonés|gallego|lenguas\s(co?\-?)?oficiales)\b", clau1, regex.I):
                        leng_alter = clau1
                    raw3 = raw2[prev_clau_i:]
            else:
                tema0 = regex.findall(r"([^\.]*\W(tem[áa]\w*(?!\sdel\smensaje)|trat(e|ar)\s(sobre|acerca)|reflej|vers(e|ar))[^\.]*)", raw2, regex.I)
                tema = tema0[0][0] if tema0 else "N/A"
                extension0 = regex.findall(r"([^\.]*\W(palabras|folio|líneas|caracteres|extensi[oó]n|longitud)[^\.]*)", raw2, regex.I)
                extension = extension0[0][0] if extension0 else "N/A"
                formato0 = regex.findall(r"([^\.]*\W(formato|tamaño|letra|interlineado|arial|times\s\new\s\roman)[^\.]*)", raw2, regex.I)
                formato = formato0[0][0] if formato0 else "N/A"
                leng_alter0 = regex.findall(r"([^\.]*\W(catalán|eusquera|aragonés|valenciano|gallego|lenguas\s(co?\-?)?oficiales)[^\.]*)", raw2, regex.I)
                leng_alter = leng_alter0[0][0] if leng_alter0 else "N/A"
    
        else:
            tema0 = regex.findall(r"([^\.]*\W(tem[áa]\w*(?!\sdel\smensaje)|trat(e|ar)\s(sobre|acerca)|reflej|vers(e|ar))[^\.]*)", raw2, regex.I)
            tema = tema0[0][0] if tema0 else "N/A"
            extension0 = regex.findall(r"([^\.]*\W(palabras|folio|líneas|caracteres|extensi[oó]n|longitud)[^\.]*)", raw2, regex.I)
            extension = extension0[0][0] if extension0 else "N/A"
            formato0 = regex.findall(r"([^\.]*\W(formato|tamaño|letra|interlineado|arial|times\s\new\s\roman)[^\.]*)", raw2, regex.I)
            formato = formato0[0][0] if formato0 else "N/A"
            leng_alter0 = regex.findall(r"([^\.]*\W(catalán|eusquera|aragonés|valenciano|gallego|lenguas\s(co?\-?)?oficiales)[^\.]*)", raw2, regex.I)
            leng_alter = leng_alter0[0][0] if leng_alter0 else "N/A"
    
        plica0 = regex.findall(r"([^\.]*\Wplica\W[^\.]*)", raw2, regex.I)
        plica = plica0[0][0] if plica0 else "N/A"
        
        
        dicto_keys = [("fecha de vencimiento", expiration_date),
                      ("envío por email", via_mail),
                      ("dirección de envío", sending_address),
                      ("país convocante", country),
                      ("fecha de vencimiento", entity),
                      ("restricciones", restrictions),
                      ("premio", price),
                      ("género", gender),
                      ("tema", tema),
                      ("extensión", extension),
                      ("formato", formato),
                      ("plica", plica),
                      ("otros idiomas", leng_alter)]

        concursos_dict_n["nombre"] = name
        concursos_dict_n["raw"] = raw2
        
        for key_name, val in dicto_keys:
            concursos_dict_n[key_name] = regex.sub(r"^\W+|[\n\s]+$", "", val) if isinstance(val, str) else val
    
        return concursos_dict_n
    
    
    def downloading_contest_info(self):
        
        resp = self._get_proxies(self.url)
        soup = bs(resp.content, "html.parser")
        content = soup.find(id="cuento") 
    
        n = 0
        self.naked_bases = {}
        for mes in content.find_all("ul"):
            for concurso in tqdm(mes.find_all("li")):
                n += 1
                name = regex.sub(r"(?<=\)).*", "", concurso.find("span").text)
                date = regex.search(r"\d{2}:\d{2}:\d{4}", concurso.text).group()
                cond_mail = concurso.find("img")
                cond_spain = regex.search(r"España", concurso.text)
                cond_age = regex.search(r"Abierto\sa\:\s(\w+\,?\s)*((menores\sde|y)\s([123]\d|diec|veint|treint)|(mayores\sde)\s([4567]\d|cuarent|cincuenta|se[ts]enta))|(nacidos?\sentre\s(\w+\s)*\d\.?\d+(\-|\sy\s)\d\.?\d+)", concurso.text)
                cond_resid = regex.search(r"Abierto\sa\:\s(\w+\,?\s)*(municipio|provincia|[Cc]omunidad\s[Aa]ut|ciudad|empadronad)", concurso.text)
                cond_alumn = regex.search(r"Abierto\sa\:\s(\w+\,?\s)*(alumno|estudiante|matriculad)", concurso.text)
                
                input_params = {}                    
                input_params["name"] = name
                input_params["date"] = date
                input_params["allows_mail"] = bool(cond_mail)
                input_params["from_spain"] = bool(cond_spain)
                input_params["has_age_restriction"] = bool(cond_age)
                input_params["has_residency_restriction"] = bool(cond_resid)
                input_params["has_student_restriction"] = bool(cond_alumn)
                
                # input_params["cumple_condiciones"] = True if (input_params.get("allows_mail") and input_params.get("from_spain") and not (input_params.get("has_age_restriction") or input_params.get("has_residency_restriction") or input_params.get("has_student_restriction"))) else False
                if input_params.get("allows_mail"):
                    url = "https://www.escritores.org"+concurso.find("a")["href"]
                    resp0 = self._get_proxies(url)
                    while_n = 0
                    while not (resp0 or while_n >= 5):
                        time.sleep(5)
                        resp0 = self._get_proxies(url)
                        while_n += 1
            
                    if resp0:
                        mini_soup = bs(resp0.content, "html.parser")
                        # Cleaning string
                        input_params["regex_out"] = self.relevant_info_retriever(mini_soup) 
                        input_params["raw"] = input_params["regex_out"].pop("raw")
                        input_params["url"] = url
                        input_params["regex_out_keys"] = list(input_params.get("regex_out").keys())
                        self.naked_bases[n] = input_params
                        
        return self
            

    def generate_chatgpt_story_rules(self, input_params):
        
        chatgpt_resp_bases = self.chatGPT.query_blank_slate(self.prompts.get("extraer_bases").format(**input_params), model="gpt-4o-mini")
                
        keys = list(input_params["regex_out"].keys())
        end_ch, end_ch0 = 0, 0
        concursos_dict = {}
        for i, e in enumerate(keys):
            end_ch = (regex.search(regex.compile(keys[i+1]), chatgpt_resp_bases).start() 
                      if (i+1 < len(keys)-1 and regex.search(regex.compile(keys[i+1]), chatgpt_resp_bases)) 
                      else (end_ch + regex.search(r"\n+", chatgpt_resp_bases[end_ch:]).end() 
                            if regex.search(r"\n+", chatgpt_resp_bases[end_ch:]) else end_ch))
            start_ch = regex.search(regex.compile(regex.escape(e)), chatgpt_resp_bases).end() if regex.search(regex.compile(regex.escape(e)), chatgpt_resp_bases) else end_ch0
            concursos_dict[e] = regex.sub(r"^\W+|(\W\,[\n\s]*)?\W$|[\n\s]*$", "", chatgpt_resp_bases[start_ch: end_ch])
            end_ch0 = end_ch
    
        input_params["bases"] = concursos_dict
    
        return input_params
            
    
    def rules_dict_cleaner(self, input_params):
        output_dict = {}
        for k, v in input_params.items():
            key = unidecode(k)
            if (k != "raw" and isinstance(v, str) or isinstance(v, bool)):
                output_dict[key] = v
            elif isinstance(v, dict) and regex.search(r"bases|regex_out", k):
                for k1, v1 in v.items():
                    output_dict[f"{key}_"+unidecode(regex.sub(r"\s", "_", k1))] = v1
        
        clean_name0 = sorted([e for e in set([input_params.get("regex_out").get("nombre"), input_params.get("bases").get("nombre"), input_params.get("name")]) if e], key=len)[0]
        output_dict["clean_name"] = regex.sub(r"\s\([A-Z]\w+.*$", "", regex.sub(r"[\\\/]+", "", clean_name0))
        
        ucols = [e for e in set(list(map(lambda x: regex.sub(r"^(regex_out|bases)_", "", x) if regex.search(r"^(regex_out|bases)_", x) and not regex.search(r"nombre", x) else None, output_dict.keys()))) if e]
        
        cleaned_params = {}
        for col in ucols:
            similar_info = [e for e in output_dict.keys() if regex.search(col, e) and output_dict.get(e)]
            if similar_info:
                if len(similar_info) == 2:
                    both_opts = [e for e in (output_dict.get(similar_info[0]).strip(), output_dict.get(similar_info[1]).strip()) if e and len(e)>1 and not regex.search(r"^\W*(n\/a|null|none)\W*$", str(e), regex.I)]
                    if both_opts:
                        cleaned_params[col] = sorted(list(set(both_opts)), key=len)[0]
                elif  len(similar_info) == 1:
                    cleaned_params[col] = output_dict.get(similar_info[0]).strip()

        date_date = dt.strptime(regex.sub(r"\s*", "", input_params.get("date")), '%d:%m:%Y').date()
        try:
            fecha_date = dt.strptime(regex.sub(r"\s?[\-\/]s?", ":", cleaned_params.get("fecha_de_vencimiento")), '%d:%m:%Y').date()
            final_date = max(fecha_date, date_date)
        except:
            final_date = date_date
            
        cleaned_params["fecha_de_vencimiento"] = final_date
                
        not_double_entries = {key: regex.sub(u"\xa0", "", v) for key, v in output_dict.items() if isinstance(v, str) and not regex.search(r"^(raw|regex|bases|date|nombre|name|has_|allows_mail)", key)}
        cleaned_params.update(not_double_entries)

        return cleaned_params


    def get_ruled_contests(self):
                
        if not self.final_bases:
            if os.path.exists(self.bases_path):
               self.final_bases = _read_file(self.bases_path)
            else:
                if not self.naked_bases:
                    if os.path.exists(self.naked_bases_path):
                       self.naked_bases = _read_file(self.naked_bases_path)
                    else:
                        print("\nDownloading the contests' information and extracting its rules with regex...\n")
                        self.downloading_contest_info()
                        _write_file(self.naked_bases, self.naked_bases_path)
                    
                    print("\nAsking ChatGPT for the rules of each contest...\n")
                    self.final_bases = {}
                    self.suspicious_conts = []
                    for ncontest, input_params in self.naked_bases.items(): 
                        cond_long_raw = input_params.get("raw") and (len(input_params.get("raw")) > len(input_params.get("name"))*5)
                        if cond_long_raw:
                            input_params1 = self.generate_chatgpt_story_rules(input_params)
                            cleaned_params = self.rules_dict_cleaner(input_params1)
                            self.final_bases[ncontest] = cleaned_params
                        
                    _write_file(self.final_bases, self.bases_path)
            
        return self
    
    

    
    # def submit_story(self, gdriver, story, author):
    #     story.generate_file(gdriver, self.formatting)
    #     send_email(target = self.email, 
    #                sender_name = author.get("name"), 
    #                sender_email = author.get("email"), 
    #                subject = self.subject, 
    #                body = "Adjunto documentos para participar en el " + self.name, 
    #                attachment_loc = story.story_uuid, 
    #                attachment_name = story.title+self.formatting["extension"])
        
