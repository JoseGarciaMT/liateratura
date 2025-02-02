#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 10:27:55 2024

@author: josegmt
"""

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


from markdown import markdown

import os, sys
import json


from google.oauth2.service_account import Credentials 
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from DatabaseConnector import _write_file, _read_file


root_path = os.path.dirname(os.path.dirname(__file__))
token_path = os.path.join(root_path,"secrets", "service_account.json") 

class GDriveManager:        
        
    def __init__(self):
        gauth = GoogleAuth()

        settings = {
            "client_config_backend": "service",
            "service_config": {
                "client_json_file_path": "service_account.json"}
                }
        # Create instance of GoogleAuth
        gauth = GoogleAuth(settings=settings)
        gauth.ServiceAuth()

        self.drive = GoogleDrive(gauth)
        
        auth_json = _read_file(token_path)
        self.creds = Credentials.from_service_account_info(json.loads(auth_json))
        
                
    def generate_gdoc_from_text(self, title, text, filename, formatting = {"font_family":"arial","font_size":"11","line-height":"1.5"}):

        mkdown = "## **" + title + "**" + \
            "\n\n <p style=\"font-size:" + formatting.get("font_size") + ";" \
                +"font-family:" + formatting.get("font_family") + ";" \
                +"line-height:" + formatting.get("line-height") + "\">" + text + "</p>"
        htmldoc = markdown(mkdown)
    
        gdoc = self.drive.CreateFile(
            {
                "title": filename+".docx",
                "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            }
        )
        gdoc.SetContentString(htmldoc)
        gdoc.Upload(param={'convert': True})
        
        return gdoc.get("id")
    
    
    def download_file_from_gdoc(self, gdoc_id, filename, mimeType="application/pdf"):
    
        try:
            service = build('drive', 'v3', credentials=self.creds)
            data = service.files().export(fileId=gdoc_id, mimeType=mimeType).execute()
            if data:
                _write_file(data, filename)
                    
        except HttpError as error:
            print(F'An error occurred: {error}', file=sys.stderr)
            
        return data
    
