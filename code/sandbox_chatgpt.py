#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 12:10:03 2024

@author: josegmt
"""

from ChatGPT import ChatGPT

chatGPT = ChatGPT()

cuento = chatGPT.query("cuentame un cuento divertido de 300 palabras")

print(cuento)

cuento2 = chatGPT.query("ese no me ha gustado, haz uno totalmente distinto, para adultos")


print("\n+++++++++++++++++++++++\n")

print(cuento2)