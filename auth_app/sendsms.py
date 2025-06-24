from Remit_Assure.package import *
import json
from django.conf import settings
import requests
import sys
from twilio.rest import Client
import phonenumbers
from urllib.parse import urlencode
from Remit_Assure.helpers import *

def comma_separated(send_amount, receive_amount, exchange_rate):
    if send_amount ==  None or send_amount == "":
        send_amount = 0
    if receive_amount == None or receive_amount == "":
        receive_amount = 0
    send_amount = str(send_amount).replace(",","")
    receive_amount = str(receive_amount).replace(",","")
    if '.' in str(send_amount):
        amount = float(send_amount)
    else:
        amount = int(send_amount)
    if float(amount) > float(1) or float(amount) == float(1):
        amount = "{0:,.2f}".format(amount)
    else:
        amount = "{:.4f}".format(amount) 
    if '.' in str(receive_amount):
        receive_amount = float(receive_amount)
    else:
        receive_amount = int(receive_amount)
    if float(receive_amount) > float(1) or float(receive_amount) == float(1):
        receive_amount = "{0:,.2f}".format(receive_amount)
    else:
        receive_amount = "{:.4f}".format(receive_amount) 
    if exchange_rate != None:
        exchange_rate = str(exchange_rate).replace(",","")
        if float(exchange_rate) > float(1) or float(exchange_rate) == float(1):           
            exchange_rate = "{:.2f}".format(float(exchange_rate))
    return {'send_amount':amount, 'receive_amount':receive_amount,'exchange_rate':exchange_rate}


def send_sms(mobile,otp):
    if settings.SEND_OTP == True: 
        message="Dear customer, your OTP (One Time Password) is "+str(otp)
        data = {'Body': message, 'To': mobile, 'From': settings.TWILIO_SENDER_ID }
        client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)
        url =  str(settings.TWILIO_URL)+"/"+str(settings.TWILIO_SID)+"/Messages.json"
        payload = urlencode(data)        
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'Basic '+str(settings.TWILIO_ACCESS_TOKEN) }
        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
    else:
        return otp

""" Twilio api to send sms """
def twilio_send_sms(message):
    data = {'Body': message, 'To': str(settings.REMIT_ASSURE_MOBILE), 'From': settings.TWILIO_SENDER_ID }
    client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)
    url =  str(settings.TWILIO_URL)+"/"+str(settings.TWILIO_SID)+"/Messages.json"
    payload = urlencode(data)        
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'Basic '+str(settings.TWILIO_ACCESS_TOKEN) }
    response = requests.request("POST", url, headers=headers, data=payload)
    response = response.json()
    return response

""" Sending sms notification to WidophRemit """
def send_sms_to_RA(type, data):
    try:
        if settings.SEND_OTP == True:
            if type == "customer":
                message="New user has signed up with "+str(data['email'])
            elif type == "transaction":
                amount = replace_comma(data['amount'])
                exchange_rate = replace_comma(data['exchange_rate'])
                amount = float_int(amount)
                amount = comma_value(amount)
                message= str(data['customer_id'])+" has created a new transaction with Transaction ID: "+str(data['transaction_id'])+" and payment status: "+str(data['payment_status'])+" for "+str(data['send_currency'])+" "+str(amount)+" (FX "+str(exchange_rate)+")"      
            response = twilio_send_sms(message)
            return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(str(e)+" in line "+str(exc_tb.tb_lineno)+" in send sms to Ra")

def send_sms_to_RA_transaction_webhook(type,data):
    try:
        if settings.SEND_OTP == True:
            amount = str(data['amount']).replace(",","")
            exchange_rate = str(data['exchange_rate']).replace(",","")
            if '.' in str(amount):
                amount = float(amount)
            else:
                amount = int(amount)
            if float(amount) < float(1):
                amount = "{:.4f}".format(amount) 
            else:
                amount = f"{amount:,}"
            message= "Updated Payment status for Transaction ID: "+str(data['transaction_id'])+" is "+str(data['payment_status'])+" for "+str(data['send_currency'])+" "+str(amount)+" (FX "+str(exchange_rate)+")"
            data = {'Body': message, 'To': str(settings.REMIT_ASSURE_MOBILE), 'From': settings.TWILIO_SENDER_ID }
            client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)
            url =  str(settings.TWILIO_URL)+"/"+str(settings.TWILIO_SID)+"/Messages.json"
            payload = urlencode(data)        
            headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'Basic '+str(settings.TWILIO_ACCESS_TOKEN) }
            response = requests.request("POST", url, headers=headers, data=payload)
            response = response.json()
            return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(str(e)+" in line "+str(exc_tb.tb_lineno))

def send_sms_to_recipient(data, recipient_mobile):
    try:
        if settings.SEND_OTP == True:
            receive_amount = str(data['receive_amount']).replace(",","")
            if '.' in str(receive_amount):
                receive_amount = float(receive_amount)
            else:
                receive_amount = int(receive_amount)
            if float(receive_amount) < float(1):
                receive_amount = "{:.4f}".format(receive_amount) 
            else:
                receive_amount = f"{receive_amount:,}"
            if str(data['username']) == "":
                user = data['email']
            else:
                user = data['username']
            message= "Good news from WidophRemit! "+str(user)+" sent you "+str(data['receive_currency'])+" "+str(receive_amount)+" and your bank account should be credited within 2-3 working days."
            data = {'Body': message, 'To': str(recipient_mobile), 'From': settings.TWILIO_SENDER_ID }
            client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)
            url =  str(settings.TWILIO_URL)+"/"+str(settings.TWILIO_SID)+"/Messages.json"
            payload = urlencode(data)        
            headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'Basic '+str(settings.TWILIO_ACCESS_TOKEN) }
            response = requests.request("POST", url, headers=headers, data=payload)
            response = response.json()
            return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(str(e)+" in line "+str(exc_tb.tb_lineno))

def send_sms_to_customer(data, user_mobile, type):
    try:
        if settings.SEND_OTP == True:
            amount = str(data['send_amount']).replace(",","")
            if '.' in str(amount):
                amount = float(amount)
            else:
                amount = int(amount)
            if float(amount) < float(1):
                amount = "{:.4f}".format(amount) 
            else:
                amount = f"{amount:,}"
            if str(type).lower() == "customer": #when widophremit receive funds
                message= "Hi! Your payment to WidophRemit for "+str(data['send_currency'])+" "+str(amount)+" has been received. We will be in touch soon to confirm settlement. Thank you."
            if str(type).lower() == "recipient": #when widophremit will send funds to beneficiary
                message= "Hi! Your WidophRemit transfer for "+str(data['send_currency'])+" "+str(amount)+" for transfer "+str(data['transaction_id'])+" has been paid to your nominated account. Thank you."
            
            data = {'Body': message, 'To': str(user_mobile), 'From': settings.TWILIO_SENDER_ID }
            client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)
            url =  str(settings.TWILIO_URL)+"/"+str(settings.TWILIO_SID)+"/Messages.json"
            payload = urlencode(data)        
            headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'Basic '+str(settings.TWILIO_ACCESS_TOKEN) }
            response = requests.request("POST", url, headers=headers, data=payload)
            response = response.json()
            return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(str(e)+" in line "+str(exc_tb.tb_lineno))

# Bulk sms
# def send_sms(mobile,otp):
#     if settings.SEND_OTP == True:    
#         message="Dear customer, your OTP (One Time Password) is "+str(otp)
#         url = "https://api.bulksms.com/v1/messages"
#         payload = json.dumps({
#         "from": settings.SENDER_ID,
#         "to": str(mobile),
#         "body": str(message)
#         })
#         headers = {
#         'Authorization': 'Basic '+settings.SMS_TOKEN,
#         'Content-Type': 'application/json'
#         }
#         response = requests.request("POST", url, headers=headers, data=payload)
#         response = response.json()
#         return response
#     else:
#         return otp

# def send_sms_to_RA(type,data):
#     try:
#         if settings.SEND_OTP == True:
#             amount = str(data['amount']).replace(",","")
#             exchange_rate = str(data['exchange_rate']).replace(",","")
#             if '.' in str(amount):
#                 amount = float(amount)
#             else:
#                 amount = int(amount)
#             if float(amount) < float(1):
#                 amount = "{:.4f}".format(amount) 
#             else:
#                 amount = f"{amount:,}"
#             if type == "customer":
#                 message="New user has signed up with "+str(data['email'])
#             elif type == "transaction":
#                 message= str(data['customer_id'])+" has created a new transaction with Transaction ID: "+str(data['transaction_id'])+" and payment status: "+str(data['payment_status'])+" for "+str(data['send_currency'])+" "+str(amount)+" (FX "+str(exchange_rate)+")"
#             url = "https://api.bulksms.com/v1/messages"
#             payload = json.dumps({
#             "from": settings.SENDER_ID,
#             "to": str(settings.REMIT_ASSURE_MOBILE),
#             "body": str(message),
#             "encoding":"UNICODE",
#             })
#             headers = {
#             'Authorization': 'Basic '+settings.SMS_TOKEN,
#             'Content-Type': 'application/json'
#             }
#             response = requests.request("POST", url, headers=headers, data=payload)
#             response = response.json()
#             return response
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         print(str(e)+" in line "+str(exc_tb.tb_lineno))
    
# def send_sms_to_RA_transaction_webhook(type,data):
#     try:
#         if settings.SEND_OTP == True:
#             amount = str(data['amount']).replace(",","")
#             exchange_rate = str(data['exchange_rate']).replace(",","")
#             if '.' in str(amount):
#                 amount = float(amount)
#             else:
#                 amount = int(amount)
#             if float(amount) < float(1):
#                 amount = "{:.4f}".format(amount) 
#             else:
#                 amount = f"{amount:,}"
#             message= "Updated Payment status for Transaction ID: "+str(data['transaction_id'])+" is "+str(data['payment_status'])+" for "+str(data['send_currency'])+" "+str(amount)+" (FX "+str(exchange_rate)+")"
#             url = "https://api.bulksms.com/v1/messages"
#             payload = json.dumps({
#             "from": settings.SENDER_ID,
#             "to": str(settings.REMIT_ASSURE_MOBILE),
#             "body": str(message),
#             "encoding":"UNICODE",
#             })
#             headers = {
#             'Authorization': 'Basic '+settings.SMS_TOKEN,
#             'Content-Type': 'application/json'
#             }
#             response = requests.request("POST", url, headers=headers, data=payload)
#             response = response.json()
#             return response
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         print(str(e)+" in line "+str(exc_tb.tb_lineno))

# def send_sms_to_recipient(data, recipient_mobile):
#     try:
#         if settings.SEND_OTP == True:
#             receive_amount = str(data['receive_amount']).replace(",","")
#             if '.' in str(receive_amount):
#                 receive_amount = float(receive_amount)
#             else:
#                 receive_amount = int(receive_amount)
#             if float(receive_amount) < float(1):
#                 receive_amount = "{:.4f}".format(receive_amount) 
#             else:
#                 receive_amount = f"{receive_amount:,}"
#             message= "Good news from WidophRemit! "+str(data['username'])+" sent you "+str(data['receive_currency'])+" "+str(receive_amount)+" and your bank account should be credited within 2-3 working days."
#             url = "https://api.bulksms.com/v1/messages"
#             payload = json.dumps({
#             "from": settings.SENDER_ID,
#             "to": str(recipient_mobile),
#             "body": str(message),
#             "encoding":"UNICODE",
#             })
#             headers = {
#             'Authorization': 'Basic '+settings.SMS_TOKEN,
#             'Content-Type': 'application/json'
#             }
#             response = requests.request("POST", url, headers=headers, data=payload)
#             response = response.json()
#             print(response)
#             return response
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         print(str(e)+" in line "+str(exc_tb.tb_lineno))

# def send_sms_to_customer(data, user_mobile, type):
#     try:
#         if settings.SEND_OTP == True:
#             amount = str(data['send_amount']).replace(",","")
#             if '.' in str(amount):
#                 amount = float(amount)
#             else:
#                 amount = int(amount)
#             if float(amount) < float(1):
#                 amount = "{:.4f}".format(amount) 
#             else:
#                 amount = f"{amount:,}"
#             if str(type).lower() == "customer": #when widophremit received funds
#                 message= "Hi! Your payment to WidophRemit for "+str(data['send_currency'])+" "+str(amount)+" has been received. We will be in touch soon to confirm settlement. Thank you."
#             if str(type).lower() == "recipient": #when widophremit will send funds to beneficiary
#                 message= "Hi! Your WidophRemit transfer for "+str(data['send_currency'])+" "+str(amount)+" for transfer "+str(data['transaction_id'])+" has been paid to your nominated account. Thank you."
#             url = "https://api.bulksms.com/v1/messages"
#             payload = json.dumps({
#             "from": settings.SENDER_ID,
#             "to": str(user_mobile),
#             "body": str(message),
#             "encoding":"UNICODE",
#             })
#             headers = {
#             'Authorization': 'Basic '+settings.SMS_TOKEN,
#             'Content-Type': 'application/json'
#             }
#             response = requests.request("POST", url, headers=headers, data=payload)
#             response = response.json()
#             return response
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         print(str(e)+" in line "+str(exc_tb.tb_lineno))


