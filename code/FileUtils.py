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

def _generate_gdoc_from_text(title, text):

    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    text = "## "+title+"\n\n"+text
    htmldoc = markdown(text)

    gdoc = drive.CreateFile(
        {
            "title": title+".doc",
            "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }
    )
    gdoc.SetContentString(htmldoc)
    gdoc.Upload(param={'convert': True})
    
    return gdoc.get("id")
    
    
def _download_file_from_gdoc(gdoc_id, filename, mimeType="application/pdf"):
    SCOPES = ['https://www.googleapis.com/auth/drive']

    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('credentials.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)
        data = service.files().export(fileId=gdoc_id, mimeType=mimeType).execute()
        if data:
            with open(filename, 'wb') as target_file:
                target_file.write(data)
                
    except HttpError as error:
        print(F'An error occurred: {error}')

def text_to_pdf_file(title, text, filename):
    gdoc_id = _generate_gdoc_from_text(title, text)
    filename = filename.replace(".doc", ".pdf")
    _download_file_from_gdoc(gdoc_id, filename, "application/pdf")

def text_to_docx_file(title, text, filename):
    gdoc_id = _generate_gdoc_from_text(title, text)
    filename = filename.replace(".doc", ".docx")
    _download_file_from_gdoc(gdoc_id, filename, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    
