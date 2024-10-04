#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 09:33:14 2024

@author: josegmt
"""


import os
from openai import OpenAI
from dotenv import load_dotenv

class ChatGPT:
    
    def __init__(self):
        load_dotenv()
        api_key = os.environ['OPENAI_API_KEY']
        self.client = OpenAI(
          api_key = api_key,
          organization = 'org-5D09KgstcTGuB0R3ya4A5wwC',
          project = 'proj_qAerChpO0bWKE2Xa8dhofBu5'
        )
        
        return None
         

    def query(self, input_query, model="gpt-4o-mini"):
        response = self.client.chat.completions.create(model = model,
                                                  messages = [{"role": "user", "content": input_query}]
        )
            
            
        return response.choices[0].message.content