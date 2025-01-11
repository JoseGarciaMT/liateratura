#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 12:10:03 2024

@author: josegmt
"""

from ChatGPT import ChatGPT

chatGPT = ChatGPT()

cuento = chatGPT.query("cuentame un cuento divertido de 100 palabras")

print(cuento)

cuento2 = chatGPT.query("ese no me ha gustado, haz uno totalmente distinto, para adultos")


print("\n+++++++++++++++++++++++\n")

print(cuento2)

print("\n+++++++++++++++++++++++\n")
print("Resultado con chatGPT.query: "+chatGPT.query("¿Cuantos cuentos me has contado?"))
print("\n+++++++++++++++++++++++\n")
print("Resultado con chatGPT.query_blank_slate: "+chatGPT.query_blank_slate("¿Cuantos cuentos me has contado?"))