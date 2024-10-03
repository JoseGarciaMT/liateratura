#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 12:06:57 2024

@author: josegmt
"""

from EmailUtils import sendEmail

sendEmail("chupirrita@gmail.com",
          {"name":"Gerardo Pérez Trías", "email":"gerardopereztrias@gmail.com"},
          "Inscripción en concurso XYZ",
          "Aquí va el texto del email",
          "cuento.pdf"
          )