#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 16:43:52 2024

@author: josegmt
"""

import os
import uuid
import joblib

class Plica():
    
    def __init__(self, story, author):
        
        self.plica_uuid = uuid.uuid4()
        self.story_uuid = story.story_uuid
        
        
    def save(self):
        joblib_filename = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                "data", 
                                "plicas",
                                self.story_uuid+".joblib"
                                )
        
        joblib.dump(self,joblib_filename)
        
        
    def load_story(story_uuid):
        joblib_filename = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                "data", 
                                "plicas",
                                story_uuid+".joblib"
                                )
        plica = joblib.load(joblib_filename)
        return plica