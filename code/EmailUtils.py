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


app_password_gmail = "fnrz qqwk bfpb treo"


def send_email(target, sender_name, sender_email, subject, 
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