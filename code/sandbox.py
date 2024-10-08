#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 12:06:57 2024

@author: josegmt
"""

import os

from ChatGPT import ChatGPT
from GDriveManager import GDriveManager
from EmailUtils import send_email


gdriver = GDriveManager()

chatGPT = ChatGPT()
story = chatGPT.query("Escríbeme un microrrelato en español de no más de 120 palabras que empiece por la frase 'Se acercó al mostrador' y que esté ambientado en una farmacia. Quiero que el microrrelato suene inteligente, y que alabe las virtudes de los farmacéuticos.")
title = chatGPT.query("Ahora dame el título ideal para este relato corto:\n"+story)

title = title.replace("\"", "").replace("*","")

filename = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", title+".pdf")

gdriver.text_to_pdf_file(title, story, filename)

send_email(target = "jose.garcia.mt@gmail.com",
          sender_name = "Gerardo Pérez Trías",
          sender_email = "gerardopereztrias@gmail.com",
          subject = "Inscripción en concurso XYZ",
          body = "Aquí va el texto del email",
          attachment_loc = filename,
          attachment_name = title+".pdf"
          )




