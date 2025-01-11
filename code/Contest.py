#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 13 10:08:25 2024

@author: josegmt
"""

import uuid

from ChatGPT import ChatGPT
from Story import Story
from Plica import Plica
from EmailUtils import send_email

class Contest:
    
    def __init__(self, name, email, subject, ambient, min_words, max_words,
                 font_family, font_size, line_height, extension):
        
        self.contest_uuid = uuid.uuid4()
        
        self.name = name
        self.email = email
        self.subject = subject
        
        self.ambient = ambient
        self.min_words = min_words
        self.max_words = max_words
        self.formatting = {}
        self.formatting["font_family"] = font_family
        self.formatting["font_size"] = font_size
        self.formatting["line-height"] = line_height
        self.formatting["extension"] = extension
        
        self.chatGPT = ChatGPT()
        
        self.story_list = []
        
        
    def generate_story(self):
        story = Story(chatGPT = self.chatGPT, contest_uuid = self.contest_uuid, 
                      ambient = self.ambient, min_words = self.min_words,
                      max_words = self.max_words)
        
        story.save()
        
        self.story_list.append(story.story_uuid)
        return story
    
    
    def generate_plica(self, story, author):
        plica = Plica()
        plica.save()
        
        return plica
        
    
    def submit_story(self, gdriver, story, author):
        story.generate_file(gdriver, self.formatting)
        send_email(target = self.email, 
                   sender_name = author.get("name"), 
                   sender_email = author.get("email"), 
                   subject = self.subject, 
                   body = "Adjunto documentos para participar en el " + self.name, 
                   attachment_loc = story.story_uuid, 
                   attachment_name = story.title+self.formatting["extension"])
        
