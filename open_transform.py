import os
import extract_msg
import pandas as pd
import openpyxl
from datetime import datetime
import re

PATH = "example_mails"
TODAY = datetime.today().strftime('%Y-%m-%d')

df = pd.DataFrame(columns=['email', 'save_email', 'save_time', 'get_quote_email', 'get_quote_time', 'get_quote_gwp',
                           'sale_email', 'sale_time', 'sale_gwp'])

"""
crawl the folder and return the file names
"""

def folder_crawler():
    for root, dir_names, file_names in os.walk(PATH):
        return file_names

"""
open the list of messages and find the subject, received time, receiver
Then check if the message is saved, quote or sale and add it to the relevant dimension in the dataframe
Within each check, a check is included to see if the user has previously saved or quoted. If yes, no new row is created.  
"""
def open_transform_message(emails):
    for message in emails:
        msg = extract_msg.MessageBase(PATH + "/" + str(message)) #extract the message + meta data
        subject = msg.subject #get subject
        received_time = msg.receivedTime #get received time
        received_time = received_time.strftime('%Y-%m-%d') #clean received time
        receiver = msg.to #get receive email
        body = msg.body #get body of email
        email_check = df.index[df['email']==receiver].tolist() #check if email address is in df

        

        if "individuelle Konfiguration" in subject:
            if len(email_check) > 0:
                df.at[email_check[0],'save_email'] = df.at[email_check[0],'save_email'] + 1
                df.at[email_check[0],'save_time'] = received_time
            else:
                new_data = {'email' : receiver, 'save_email' : 1, 'get_quote_email' : 0, 'sale_email' : 0,
                            'save_time': received_time}
                df.loc[len(df)] = new_data

        if "Ihr Angebot" in subject:
            
            if len(email_check) > 0:
                df.at[email_check[0],'get_quote_email'] = df.at[email_check[0],'get_quote_email'] + 1
                df.at[email_check[0],'get_quote_time'] = received_time
            else:
                payment = total_payment(body) 
                new_data = {'email' : receiver, 'save_email' : 0, 'get_quote_email' : 1, 'sale_email' : 0,
                            'get_quote_time' : received_time, 'get_quote_gwp' : payment}
                df.loc[len(df)] = new_data 
                      

        if "Bestätigung Ihres Abschlusses" in subject and "CIO" not in subject:
            if len(email_check) > 0:
                df.at[email_check[0],'sale_email'] =  1
                df.at[email_check[0],'sale_time'] =  received_time
            else:
                new_data = {'email' : receiver, 'save_email' : 0,  'get_quote_email' : 0, 'sale_email' : 1,
                            'sale_time': received_time}
                df.loc[len(df)] = new_data


def total_payment(body):
     #find payment
        payment = re.findall(r"\d+\s€\s", body)
        payment = re.split('\s', payment[0])
        payment = payment[0]
        
        #find period of payment
        period = re.findall(r"(vierteljährlich|halbjährlich|jährlich|monatlich)", body)
        period = period[0]

        #find if at or de
        country = re.findall(r"Mitteilung §§16ff VersVG AT", body)
        if len(country) > 0:
            country = 'Austria'
        else:
            country = 'Germany'
        
        #remove tax from payment
        if country == 'Germany':
            net_payment = int(payment) / 1.19
        if country == 'Austria':
            net_payment = int(payment) / 1.11

        #multiply by period
        if period == 'vierteljährlich':
            period = 4
        if period == 'jährlich':
            period = 1
        if period == 'monatlich':
            period = 12
        if period == 'halbjährlich':
            period = 2

        total_payment = net_payment * period
        total_payment = round(total_payment, 2)

        print(total_payment)

        return total_payment
"""
crawl = folder_crawler()
open_transform_message(crawl)"""