#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 10:27:55 2024

@author: josegmt
"""


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

def text_to_pdf_file(title, text, filename):
    c = canvas.Canvas(filename, pagesize=A4)
   
    textobject = c.beginText(2*cm, 29.7 * cm - 2 * cm)
    for line in text.splitlines(False):
        textobject.textLine(line.rstrip())
    c.drawText(textobject)
    c.save()
    