#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 10:27:55 2024

@author: josegmt
"""

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


from markdown import markdown

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GDriveManager:
    def _generate_gdoc_from_text(self, title, text, formatting = {"font_family":"arial","font_size":"11","line-height":"1.5"}):
    
        mkdown = "## **" + title + "**" + \
            "\n\n <p style=\"font-size:" + formatting.get("font_size") + ";" \
                +"font-family:" + formatting.get("font_family") + ";" \
                +"line-height:" + formatting.get("line-height") + "\">" + text + "</p>"
        htmldoc = markdown(mkdown)
    
        gdoc = self.drive.CreateFile(
            {
                "title": title+".doc",
                "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            }
        )
        gdoc.SetContentString(htmldoc)
        gdoc.Upload(param={'convert': True})
        
        return gdoc.get("id")
        
        
    def _download_file_from_gdoc(self, gdoc_id, filename, mimeType="application/pdf"):
    
        try:
            service = build('drive', 'v3', credentials=self.creds)
            data = service.files().export(fileId=gdoc_id, mimeType=mimeType).execute()
            if data:
                with open(filename, 'wb') as target_file:
                    target_file.write(data)
                    
        except HttpError as error:
            print(F'An error occurred: {error}')
        
        
    def __init__(self):
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        self.drive = GoogleDrive(gauth)
        
        SCOPES = ['https://www.googleapis.com/auth/drive']
        self.creds = None
    
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
    
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
        
    
    def text_to_pdf_file(self, title, text, filename):
        gdoc_id = self._generate_gdoc_from_text(title, text)
        filename = filename.replace(".doc", ".pdf")
        self._download_file_from_gdoc(gdoc_id, filename, "application/pdf")
    
    def text_to_docx_file(self, title, text, filename):
        gdoc_id = self._generate_gdoc_from_text(title, text)
        filename = filename.replace(".doc", ".docx")
        self._download_file_from_gdoc(gdoc_id, filename, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
