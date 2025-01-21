#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 12:06:57 2024

@author: josegmt
"""


from GDriveManager import GDriveManager
from Contest import Contest
from EmailUtils import send_email_gmail

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
    



# author = {"name":"Gerardo Pérez Trías", "email":"gerardopereztrias@gmail.com"}

# contest.submit_story(gdriver, story, author)


story.generate_file((gdriver))


# sender_name = "Jose GMT liateratura"
# sender_email = "jose.garcia.mt@gmail.com"
# target = ["jose.garcia.mt@gmail.com"]
# sender_pwd = "lbon gpkg wdum vhjc"
# subject = "Email Subject: PROBANDO 123"
# body = "This is the body of the text message"
# attachments = [("../data/temp/story.pdf", "titulo.pdf")] 

# send_email_gmail(target, sender_name, sender_email, sender_pwd, subject, 
#                body, attachments)