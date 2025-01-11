#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 12:06:57 2024

@author: josegmt
"""


from GDriveManager import GDriveManager
from Contest import Contest

gdriver = GDriveManager()


contest = Contest(name="Concurso X", 
                  email="info@motortor.com", 
                  subject="Me apunto al concurso X", 
                  ambient="Una farmacia",
                  min_words="300",
                  max_words="500",
                  font_family="Arial",
                  font_size="12",
                  line_height="1.5",
                  extension="pdf"
                  )

for i in range(1):
    
    story = contest.generate_story()


    print(story.metadata)
    print(story.story)
    



author = {"name":"Gerardo Pérez Trías", "email":"gerardopereztrias@gmail.com"}

contest.submit_story(gdriver, story, author)







