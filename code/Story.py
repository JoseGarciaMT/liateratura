#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 16:57:05 2024

@author: josegmt
"""

import os
import random
import uuid

import joblib

class Story:
    
    _story_query = """"Quiero que actúes como un escritor literario de prestigio con gran manejo del español a quien han encargado un cuento corto.  Dicho relato ha de cumplir las siguientes condiciones:
            - Estar ambientado en {ambient}.
            - Tener una longitud mínima de {min_words} palabras y una duración máxima de {max_words} palabras.
            - Debe ser un cuento {story_type} con un tono {tone}.
            - Debe estar escrito al estilo de {ref_author}.
            - Debe usar un lenguaje {lang_type}.
            - Debe tener {dialog_freq}
            
        Quiero que utilices guiones largos para los diálogos, siguiendo el formato que especifica este blog: https://www.correctores.es/guiones-largos/
        Por último, quiero que tengas en cuenta que se puntúa especialmente la originalidad, por lo que, si has escrito relatos previamente para mí, me gustaría que este relato sea lo más diferente posible a los relatos previos que me has dado."""
 
    _ref_author_options = ["Arturo Pérez Reverte", "Emilia Pardo Bazán", "Camilo José Cela", "Miguel de Cervantes", "Valle-Inclán", "Julio Cortázar", "Gabriel García Márquez"]
    _story_type_options = ["romántico", "de misterio", "erótico", "de aventuras", "cómico"]
    _tone_options = ["sombrío", "optimista", "sarcástico", "serio", "soez"]
    _lang_type_options = ["sencillo", "sofisticado", "soez", "muy coloquial"]
    _dialog_freq_options  = ["nada de diálogo", "poco diálogo", "mucho diálogo"]
    
    def __init__(self, chatGPT, contest_uuid, ambient, min_words, max_words):
        
        self.story_uuid = uuid.uuid4()
        self.contest_uuid = contest_uuid
        
        self.metadata = {}
        self.metadata["ambient"] = ambient
        self.metadata["min_words"] = min_words
        self.metadata["max_words"] = max_words
        self.metadata["story_type"] = random.choice(Story._story_type_options)
        self.metadata["tone"] = random.choice(Story._tone_options)
        self.metadata["ref_author"] = random.choice(Story._ref_author_options)
        self.metadata["lang_type"] = random.choice(Story._lang_type_options)
        self.metadata["dialog_freq"] = random.choice(Story._dialog_freq_options)        
        
        
        story_query = Story._story_query.format(ambient = self.metadata["ambient"],
                                                min_words = self.metadata["min_words"],
                                                max_words = self.metadata["max_words"],
                                                story_type = self.metadata["story_type"],
                                                tone = self.metadata["tone"],
                                                ref_author = self.metadata["ref_author"],
                                                lang_type = self.metadata["lang_type"],
                                                dialog_freq = self.metadata["dialog_freq"]
                                         )
        
        self.story = chatGPT.query(story_query)
        self.title = chatGPT.query("Ahora dame el título ideal para este último relato corto.")

        self.title = self.title.replace("\"", "").replace("*","")
        
        
    def generate_file(self, gdriver, contest_name,
                      formatting = {"font_family":"arial",
                                    "font_size":"11",
                                    "line-height":"1.5",
                                    "extension":".pdf"}):
        
        self.filename = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                "data", 
                                contest_name,
                                str(self.story_uuid) + formatting["extension"])
        
        if "pdf" in formatting["extension"]:
            mime = "application/pdf"
        else:
            mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            
            
        gdoc_id = gdriver.generate_gdoc_from_text(self.title, self.story, str(self.story_uuid), formatting)
        gdriver.download_file_from_gdoc(gdoc_id, self.filename, mime)
        
        return self.filename
    
    
    def save(self):
        joblib_filename = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                "data", 
                                "stories",
                                str(self.story_uuid)+".joblib"
                                )
        
        joblib.dump(self,joblib_filename)
        
        
    def load_story(story_uuid):
        joblib_filename = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                "data", 
                                "stories",
                                story_uuid+".joblib"
                                )
        story = joblib.load(joblib_filename)
        return story
            
           
        
        