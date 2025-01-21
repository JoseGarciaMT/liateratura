#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 11:50:39 2024

@author: josegmt
"""

import os
import base64
import sib_api_v3_sdk

from dotenv import load_dotenv



def send_email_sib(target, sender_name, sender_email, subject, 
               body, attachment_loc, attachment_name):
    # Instantiate the client
    configuration = sib_api_v3_sdk.Configuration()
    load_dotenv()
    configuration.api_key['api-key'] = os.environ['BREVO_API_KEY']
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    with open(attachment_loc, "rb") as file:
        encoded_string = base64.b64encode(file.read())
        base64_message = encoded_string.decode('utf-8')
    
    attachment = [{"content":base64_message,"name":attachment_name}]
    # Define the campaign settings\
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to = [{"email":target}],
        html_content = body,
        sender = {"name": sender_name, "email": sender_email},
        subject = subject,
        attachment = attachment
    )
    
    
    api_instance.send_transac_email(send_smtp_email)
    


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders


def send_email_gmail(target, sender_name, sender_email, sender_pwd, subject, 
               body, attachments=[]):
    
    msg = MIMEMultipart()
    msg.attach(MIMEText(body))
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = target
    msg['Date'] = formatdate(localtime=True)
    
    for path, filename in attachments:
        part = MIMEBase('application', "octet-stream")
        with open(path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename={}'.format(filename))
        msg.attach(part)
    
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender_email, sender_pwd)
       smtp_server.sendmail(sender_email, target, msg.as_string())

