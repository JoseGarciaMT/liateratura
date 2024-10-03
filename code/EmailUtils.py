#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 11:50:39 2024

@author: josegmt
"""

import os
import sib_api_v3_sdk

def sendEmail(target,sender,subject,body,attachments):
    # Instantiate the client
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.environ['BREVO_API_KEY']
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    # Define the campaign settings\
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to = [{"email":sender}],
        html_content = body,
        sender = { "name": sender.get("name"), "email": sender.get("email")},
        subject = subject
    )
    
    
    api_instance.send_transac_email(send_smtp_email)