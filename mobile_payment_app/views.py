from django.shortcuts import render
from Remit_Assure.package import *
from mobile_app.sendsms import *
from payment_app.models import *
from mobile_app.views import *
from Remit_Assure import settings
from payment_app.helper import *
from datetime import datetime
from mobile_payment_app.serializers import User_Profile_Serializer,Recipient_List_Serializer,Recipient_bank_detail_Serializer
# Create your views here.
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal
from weasyprint import HTML, CSS
from rest_framework import viewsets, filters
import math
import urllib.parse
from rest_framework.response import Response

import sys, os
import json
import pytz
from payment_app.views import *
from payment_app.views import get_ip,fraudnet_check_transaction,create_payment_id,update_fn_data_in_db,zai_get_user_wallet,zai_reference_number,withdraw_RA_zai_funds,get_RA_bank_details,get_RA_zai_wallet,zai_access_token,zai_token,zai_search_email_id,zai_create_user,zai_virtual_account_list,zai_create_virtual_account,zai_create_payid,zai_register_payid_peruser,zai_update_user,zai_send_money_to_wallet,zai_validate_payto_agreement,zai_get_agreement_status,zai_create_agreement,zai_agreement_start_date,zai_initiate_payment,zai_fraudnet_tranaction_check,zai_get_agreement_details,zai_update_agreement
from auth_app.views import email_to_RA
from auth_app.sendsms import send_sms_to_RA, send_sms_to_customer
from auth_app.views import forex_currency,Currency_Cloud
from payment_app.views import email_transaction_receipt,application_check
from datetime import datetime

stripe.api_key = settings.API_SECRET_KEY

stripe.api_version = "2020-08-27"

transaction = settings.TRANSACTION

#email receipt pdf to send to customer via email
def email_transaction_receipt_mobile(transaction_id, type):
    try:
       return email_transaction_receipt(transaction_id, type) 
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(str(e)+" in line "+str(exc_tb.tb_lineno))


# def email_transaction_receipt_mobile(transaction_id, type):
#     try:
#         context = {}
#         user_email = None
#         payment_status = None
#         context2_dict = {}
#         context2 = {}
#         if Transaction_details.objects.filter(transaction_id=transaction_id).exists():
#             data = Transaction_details.objects.filter(transaction_id=transaction_id).values('payment_status','transaction_id','recipient_name','send_currency', 'receive_currency','amount', 'receive_amount','date', 'reason', 'exchange_rate', 'recipient','customer_id','send_method','total_amount','discount_amount')
#             data = data[0]
#             payment_status = str(data['payment_status'])
#             date = str(data['date'])
#             date = date.replace("-","/")
#             comma =  comma_separated(send_amount=data['amount'], receive_amount=data['receive_amount'], exchange_rate=data['exchange_rate'] )
#             comma2 =  comma_separated(send_amount=data['discount_amount'], receive_amount=data['total_amount'], exchange_rate=None )
#             data['amount'] = comma['send_amount']
#             data['receive_amount'] = comma['receive_amount']
#             data['exchange_rate'] = comma['exchange_rate']
#             data['discount_amount'] = comma2['send_amount']
#             data['total_amount'] = comma2['receive_amount']
#             context = {'data': data}
#             context.update(date=date)
#             context2_dict = {"discount_amount": str(data['discount_amount']),"total_amount":data['total_amount'],"send_method":data['send_method'],"transaction_id":transaction_id,"send_currency":str(data['send_currency']).upper(), "payment_status":data['payment_status'], "amount":str(data['amount']), "exchange_rate": comma['exchange_rate'], "receive_amount":data['receive_amount'], "receive_currency":data['receive_currency']}
#             context2_dict.update(message="Here are the Transaction Details for Transaction ID: "+str(transaction_id))
#             context2.update(date=date)
#             print(data, "receipt data")
#             if User.objects.filter(customer_id=data['customer_id'], is_superuser=False).exists():
#                 customer_name = User.objects.filter(customer_id=data['customer_id'], is_superuser=False).values('email','customer_id','First_name','Last_name','id')
#                 user_id = customer_name[0]['id']
#                 user_email = customer_name[0]['email']
#                 customer_id = customer_name[0]['customer_id']
#                 customer_name = str(str(customer_name[0]['First_name'])+" "+str(customer_name[0]['Last_name']))
#                 context.update(login=settings.LOGIN_LINK, support=settings.SUPPORT_CENTER_LINK,customer_name = customer_name)
#                 context2.update(remitassure=settings.REMITASSURE_LINK,login=settings.LOGIN_LINK,support=settings.SUPPORT_CENTER_LINK,email=user_email, customer_id=customer_id, type="transaction",customer_name=customer_name,transaction=context2_dict)
#                 if User_address.objects.filter(user_id=int(user_id)).exists():
#                     a = User_address.objects.filter(user_id=int(user_id)).values('building','street','city','state','country')
#                     customer_address = str(str(a[0]['building'])+" "+str(a[0]['street'])+" "+str(a[0]['city'])+" "+str(a[0]['state'])+" "+str(a[0]['country']))
#                     context.update(customer_address = customer_address)
#             if Recipient.objects.filter(id=data['recipient']).exists():
#                 r = Recipient.objects.filter(id=data['recipient']).values('first_name','last_name','mobile','building','street','city','state','country')
#                 recipient_address = str(str(r[0]['building'])+" "+str(r[0]['street'])+" "+str(r[0]['city'])+" "+str(r[0]['state'])+" "+str(r[0]['country']))
#                 recipient_mobile = r[0]['mobile']
#                 context2.update(recipient_name=str(r[0]['first_name'])+" "+str(r[0]['last_name']))
#                 context.update(recipient_mobile=recipient_mobile,recipient_address = recipient_address)
#             if Recipient_bank_details.objects.filter(recipient_id=data['recipient']).exists():
#                 b = Recipient_bank_details.objects.filter(recipient_id=data['recipient']).values('account_number','account_name','bank_name')
#                 account_number = b[0]['account_number']
#                 context.update(account_number=account_number)
#                 context2.update(recipient_bank=b[0]['bank_name'])
#             context2.update(data= email_template_image())
#             # Render the HTML template with context
#             template = get_template('mobile_receipt.html')
#             html = template.render(context)

#             # Generate a PDF file from the HTML content
#             css = CSS(string='@page { size: A4; margin: 1cm }')
#             pdf_file = HTML(string=html).write_pdf(stylesheets=[css])

#             # Create an HTTP response with the PDF file as content, to prompt the user to download the file
#             response = HttpResponse(pdf_file, content_type='application/pdf')
#             response['Content-Disposition'] = 'attachment; filename="receipt.pdf"'

#             # Attach the PDF to the email
#             pdf_attachment = MIMEApplication(pdf_file, _subtype='pdf')
#             pdf_attachment.add_header('content-disposition', 'attachment', filename='receipt.pdf')
 
#             msg = MIMEMultipart()
#             msg['From'] = settings.EMAIL_HOST_USER
#             msg['To'] = user_email

#             if str(type).lower() == "payout":
#                 template2 = get_template('customer_payout.html')
#                 msg['Subject'] = 'Payout Confirmation for Transaction ID '+str(transaction_id)
#             else:
#                 template2 = get_template('sender_notification.html')
#                 msg['Subject'] = 'WidophRemit Transaction Confirmation'

#             # Attach the PDF to the email
#             msg.attach(pdf_attachment)

#             # Attach the HTML content as an alternative
#             html2 = template2.render(context2)
#             html_content2 = MIMEText(html2, 'html')
#             msg.attach(html_content2)

#             smtp_server = settings.EMAIL_HOST
#             smtp_port = settings.EMAIL_PORT  
#             smtp_username = settings.EMAIL_HOST_USER
#             smtp_password = settings.EMAIL_HOST_PASSWORD
#             with smtplib.SMTP(smtp_server, smtp_port) as server:
#                 server.starttls()  # Use TLS encryption
#                 server.login(smtp_username, smtp_password)
#                 server.sendmail(smtp_username, user_email, msg.as_string())
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         print(str(e)+" in line "+str(exc_tb.tb_lineno))

class Exchange_Rate_Converter(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        To = request.data.get('to')
        From = request.data.get('from')
        Amount = request.data.get('amount')
        direction = request.data.get('direction')
        if not From:
            return bad_response(message = "Please enter location" )
        if not To:
            return bad_response (message="Please enter destination")
        if Amount == None or not Amount:
            return bad_response(message="Please enter amount")
        try:
            From = str(From)
            To = str(To)
            Amount = str(Amount)
            # if user want to convert nzd to thailand
            # if From == "NZD" and To == "THB":
            #     To = "AUD"
            #     response1 = Currency_Cloud(str(From), str(To), str(Amount))
            #     first_exchange_rate = response1['rate']
            #     From = "AUD"
            #     To = "THB"
            #     response2 = Currency_Cloud(str(From), str(To), str(Amount))
            #     second_exchange_rate = response2['rate']
            #     final_exchange_rate = str(first_exchange_rate * second_exchange_rate)
            #     if '.' in final_exchange_rate:
            #         final_exchange_rate = float(final_exchange_rate)
            #         final_exchange_rate = round(final_exchange_rate, 2)
            #     else:
            #         final_exchange_rate = int(final_exchange_rate)
            #     if '.' in Amount:
            #         Amount = float(Amount)
            #     else:
            #         Amount = int(Amount)
            #     received_amount = Amount*final_exchange_rate
            #     if '.' in str(received_amount):
            #         received_amount = round(received_amount, 2)
            #     return success_response(message="success", data={'amount': str(received_amount), "rate": str(final_exchange_rate)})
            response = Currency_Cloud(str(From), str(To), str(Amount), str(direction))
            rate = str(response['rate'])
            # if '.' in rate:
            #     rate = float(rate)
            #     rate = round(rate, 1)
            # else:
            #     rate = int(rate)
            return success_response(message="success", data={'amount': str(response['amount']), "rate": str(response['rate'])})
        except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))


# class Exchange_check_view(APIView):
#     renderer_classes = [UserRenderer]
#     permission_classes=[IsAuthenticated]

#     def post(self, request, format=None):
#         try:
#             user = User_Profile_Serializer(request.user)    
#             user_serializer = user.data
#             if not request.user.id:
#                 return Response(status=status.HTTP_401_UNAUTHORIZED)
            
#             is_digital_Id_verified = user_serializer['is_digital_Id_verified']
#             if is_digital_Id_verified != "approved":
#                 return Response({"code":"400","message":"Verify Your Account."})
#             if is_digital_Id_verified == "submitted":
#                 return Response({"code":"200","message":"Your KYC has been submitted, please wait for approval ."})
            
#             #check transactions account usage limit
#             # customer_id = user_serializer["customer_id"]
#             # transa = Transaction_details.objects.filter(customer_id=customer_id).values('transaction_id')[0]
#             # transaction_id = transa['transaction_id']
#             # resposne =  payment_usage_check(request.user.id, request.user.customer_id, transaction_id)
#             # if resposne:
#             #     return bad_response(resposne)

#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))


class preferred_destination_currency_view(APIView):
    renderer_classes = [UserRenderer]
    permission_classes=[IsAuthenticated]

    def post(self, request, format=None):
        try:
            user = User_Profile_Serializer(request.user)    
            user = user.data    
            source_currency = request.data.get('source_currency')        
            destination_currency = request.data.get('destination_currency')        
            if not User.objects.filter(id = user['id'], is_superuser=False).exists():
                return bad_response(message="User does not exist") 
            if not destination_currency:
                return bad_response(message="Please enter preferred destination currency")
            if not source_currency:
                return bad_response(message="Please enter source destination currency")  
            User.objects.filter(id = user['id'], is_superuser=False).update(source_currency=str(source_currency).upper(), destination_currency=str(destination_currency).upper())
            data = User.objects.filter(id = user['id'], is_superuser=False).values('destination_currency','source_currency')
            return success_response(message= "success", data={'source_currency':data[0]['source_currency'],'destination_currency':data[0]['destination_currency']})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        
    def get(self, request, format=None):
        try:
            user = User_Profile_Serializer(request.user)    
            user = user.data    
            if not User.objects.filter(id = user['id'], is_superuser=False).exists():
                return bad_response(message="User does not exist") 
            data = User.objects.filter(id = user['id'], is_superuser=False).values('source_currency','destination_currency')
            return success_response(message= "success", data={'source_currency':data[0]['source_currency'],'destination_currency':data[0]['destination_currency']})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))



def insert_sender_details(customer_email,sender,user_id,sender_address):
    User.objects.filter(email=customer_email).update(**sender)
    sender_address.update(user_id=user_id)
    if not User_address.objects.filter(user_id=user_id).exists():
        User_address.objects.create(**sender_address)
    else:
        User_address.objects.filter(user_id=user_id).update(**sender_address)

def create_recipient(recipient, user_id, bank_details):
    recipient.update(user_id=user_id)
    recipient_id = Recipient.objects.create(**recipient)
    recipient_id = getattr(recipient_id, 'id')
    bank_details.update(recipient_id=recipient_id)
    Recipient_bank_details.objects.create(**bank_details)
    return recipient_id


class Stripe_one_step_payment_View(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        profile_serializer = User_Profile_Serializer(request.user)
        transaction_id = request.data.get("transaction_id")
        card_token = request.data.get("card_token")

        if not transaction_id:
            return bad_response(message="Please enter transaction_id")
        
        Transaction_details.objects.filter(transaction_id=transaction_id).update(payment_status=transaction['pending_payment'], card_token= card_token)

        # card type values fro fraud.net 
        card_dict = {'Visa': "visa", 'Mastercard':"mc", 'American Express':"amex", 'Discover':"discover", 'Diners Club':"diners_club"}
        try:
            if not Transaction_details.objects.filter(transaction_id=transaction_id).exists():
                return bad_response(message="Invalid transaction_id")
            
            obj = Transaction_details.objects.filter(transaction_id=transaction_id)
            obj = obj[0]
            if '.' in str(obj.amount):
                send_amount = round(float(str(obj.amount)))
            else:
                send_amount = int(str(obj.amount))
            stripe_send_amount = send_amount*100

            if not obj.recipient:
                return bad_response("Recipient not found for this transaction")     

            #getting recipien and bank details 
            if Recipient.objects.filter(id=obj.recipient).exists():
                recipient = Recipient.objects.filter(id=obj.recipient)
                #.values('flat','building','city','state','country')
                recipient = recipient[0]
                bank_data = list(Recipient_bank_details.objects.filter(recipient_id=obj.recipient).values('account_number','bank_name','swift_code','bank_address'))
                bank_dict = bank_data[0]
            else:
                return bad_response("Recipient does not exists")          
            
            if Recipient.objects.filter(id=obj.recipient).exists():
                p = Recipient.objects.filter(id=obj.recipient).values('first_name','last_name','email','mobile','flat','building','city','state','country')
                recipient_detail = p[0]
                
                
            # creating and retrieving stripe customer
            if profile_serializer.data['stripe_customer_id']:
                stripe_customer_id = profile_serializer.data['stripe_customer_id']
            else:
                stripe_customer_id = None
            try:
                search = stripe.Customer.retrieve(stripe_customer_id)
            except stripe.error.StripeError as e:
                try:
                    customer_data = stripe.Customer.create(phone=profile_serializer.data['mobile'],name= profile_serializer.data['First_name']+" "+profile_serializer.data['Last_name'], email=profile_serializer.data['email'])
                    stripe_customer_id = customer_data['id'] 
                except stripe.error.StripeError as e:
                    return bad_response(message=e.user_message)
                    
            #getting last 4 digits of card
            try:
                card_data = stripe.Token.retrieve(card_token)
                card_last4_digits = card_data['card']['last4']
                card_type_key = card_data['card']['brand']
                card_id = card_data['card']['id']
                fingerprint = str(card_data['card']['fingerprint'])
            except stripe.error.StripeError as e:
                return bad_response(message=e.user_message)
            
            if card_type_key in card_dict:
                card_type = card_dict[card_type_key]
            else:
                card_type = "other"
            if len(str(card_data['card']['exp_month'])) == 1 or len(str(card_data['card']['exp_month'])) == "1" :
                exp_date = str(0)+str(card_data['card']['exp_month'])+"-"+str(card_data['card']['exp_year'])[-2:]
            else:
                exp_date = str(card_data['card']['exp_month'])+"-"+str(card_data['card']['exp_year'])[-2:]
        
            #attachinh customer to payment method
            source_data = stripe.Customer.create_source(stripe_customer_id, source = card_token)

            #creating stripe payment Charge
            try:
                charge = stripe.Charge.create(
                customer = stripe_customer_id, 
                amount= stripe_send_amount, currency= str(obj.send_currency).upper(),
                source= card_id, description= obj.reason,
                metadata= {'name': profile_serializer.data['First_name']+" "+profile_serializer.data['Last_name'], 'customer_id': profile_serializer.data['customer_id'], 'recipient': obj.recipient_name}, 
                )         
            except stripe.error.StripeError as e:
                return bad_response(message=e.user_message)
            charge_id = charge['id']
            status = charge['status']
            fraudnet_payment_status = None
            if 'status' in charge:
                if status == "succeeded":
                    fraudnet_payment_status = "approved"         
                else:
                    fraudnet_payment_status = "cancelled"  
            print(card_type_key, "card_type_key =====================")

            if str(card_type_key).capitalize() != "Mastercard":
                card_type_key = str(card_type_key)+" Card"
            #updating charge id and payment status in transacton obj in DB
            print("trasaction_id=================", transaction_id)
            transaction_data = Transaction_details.objects.filter(transaction_id=transaction_id).update(payment_status=transaction['pending_review'],payment_gateway_transaction_id = charge_id, card_type= str(card_type_key).capitalize(), send_method= str(card_type_key).capitalize(), card_token= card_token)
        
            if User_address.objects.filter(user_id=profile_serializer.data['id']).exists():
                address = User_address.objects.filter(user_id=profile_serializer.data['id'])
                address = address[0]
                # print("*******",address)
            else:
                return bad_response(message="User Address not found")
            
            #for response
            add = User_address.objects.filter(user_id=request.user.id).values('flat','building','street','city','postcode','state','country','country_code')
            customer_add = add[0]

            #for recipient_name
            detail = Transaction_details.objects.filter(transaction_id=transaction_id).values('id','recipient_name','send_currency','receive_currency','receive_amount','exchange_rate','created_at')
            res = detail[0]
            s = detail[0]['id']
            v = detail[0]['created_at']
            d = str(s)

            #For recipient url pdf
            val="https://api.remitassure.com/mobile_payment/receipt/"
            # val="http://127.0.0.1:8000/mobile_payment/receipt/"
            url=val+d


            #for get create_date
            # v = Transaction_details.objects.filter(transaction_id=transaction_id).values('created_at').first()['created_at']
            v_datetime = datetime.strptime(str(v), '%Y-%m-%d %H:%M:%S.%f')
            date_part = v_datetime.date()
            date_val = date_part.strftime('%Y-%m-%d')

            #for get custmoer_name
            us = User.objects.filter(id=request.user.id).values('First_name', 'Last_name')
            cus_name = us[0]

            k=0
            val = User.objects.filter(id=request.user.id).values('transactions')
            # print("=====",val[0]["transactions"])
            if val[0]["transactions"]:
                k=int(val[0]["transactions"])
                k=k+1
                User.objects.filter(id=request.user.id).update(transactions=k)
            else:
                k=1
                User.objects.filter(id=request.user.id).update(transactions=k)

            #recipient data for FN
            current_time = str(timezone.now()) 
            seller_name = obj.recipient_name
            response = fraudnet_check_transaction(fingerprint=fingerprint, customer_id=str(profile_serializer.data['customer_id']), fn=str(profile_serializer.data['First_name']), ln=str(profile_serializer.data['Last_name']), address=str(address.building)+" "+str(address.street), city=str(address.city), state=str(address.state), postcode= str(address.postcode),customer_country_code= str(address.country_code).upper(), dob=str(profile_serializer.data['Date_of_birth']), mobile=str(profile_serializer.data['mobile']), email=str(profile_serializer.data['email']), recipient_id=obj.recipient, recipient_country_code=str(recipient.country_code).upper(), recipient_address=str(recipient.building)+" "+str(recipient.street)+" "+recipient.city+" "+recipient.state, recipient_name= obj.recipient_name, account_no=str(bank_data[0]['account_number']), exp_date=exp_date, card_last4_digits=card_last4_digits, payment_id=transaction_id, card_type=card_type, send_currency=obj.send_currency.upper(), send_amount=str(send_amount), receivecurrency=obj.receive_currency.upper(), fraudnet_payment_status=fraudnet_payment_status, transaction_id=obj.id)
            if 'source' in response:
                if response['source'] == "Duplicate Order":
                    tid = str(date.today())+"0"+str(tid)
                    response = fraudnet_check_transaction(fingerprint=fingerprint, customer_id=str(profile_serializer.data['customer_id']), fn=str(profile_serializer.data['First_name']), ln=str(profile_serializer.data['Last_name']), address=str(address.building)+" "+str(address.street), city=str(address.city), state=str(address.state), postcode= str(address.postcode),customer_country_code= str(address.country_code).upper(), dob=str(profile_serializer.data['Date_of_birth']), mobile=str(profile_serializer.data['mobile']), email=str(profile_serializer.data['email']), recipient_id=obj.recipient, recipient_country_code=str(recipient.country_code).upper(), recipient_address=str(recipient.building)+" "+str(recipient.street)+" "+recipient.city+" "+recipient.state, recipient_name= obj.recipient_name, account_no=str(bank_data[0]['account_number']), exp_date=exp_date, card_last4_digits=card_last4_digits, payment_id=transaction_id, card_type=card_type, send_currency=obj.send_currency.upper(), send_amount=str(send_amount), receivecurrency=obj.receive_currency.upper(), fraudnet_payment_status=fraudnet_payment_status, transaction_id=tid)
            if 'data' in response:
                update_fn_data_in_db(response=response, customer_id=str(profile_serializer.data['customer_id']), transaction_id=obj.id)
            payment_status =  Transaction_details.objects.filter(transaction_id=transaction_id).values('send_method','payment_status','id')
            
            notification.objects.create(source_id=payment_status[0]['id'], source_type="transaction", source_detail=str(send_amount)+" "+obj.send_currency, message=settings.NOTIFICATION_TRANSACTION_MSG)
            send_sms_to_RA(type="transaction",data={'transaction_id':transaction_id,'customer_id':profile_serializer.data['customer_id'],'send_currency':obj.send_currency.upper(), 'amount': str(obj.amount), 'payment_status':payment_status[0]['payment_status'],'exchange_rate':obj.exchange_rate})
            # email_to_RA(type="transaction", data={'send_method':payment_status[0]['send_method'],'transaction_id':transaction_id,'email':profile_serializer.data['email'],'customer_id':profile_serializer.data['customer_id'],'send_currency':obj.send_currency.upper(),'payment_status':payment_status[0]['payment_status'], 'amount': str(obj.amount), 'exchange_rate': obj.exchange_rate})
            email_to_RA(type="transaction", id = transaction_id)
            #sending transaction email receipt or sms to customer
            email_transaction_receipt_mobile(transaction_id=transaction_id)
            send_sms_to_customer(type= "customer",data={'transaction_id':transaction_id,'send_currency':obj.send_currency, 'send_amount':obj.amount}, user_mobile=profile_serializer.data['mobile'])
            return success_response(message=payment_status[0]['payment_status'], data={"id":str(obj.id),"status":payment_status[0]['payment_status'] ,"transaction_id":str(transaction_id),"date":date_val,"url":url,"account_number":str(bank_dict['account_number']),"swift_code":str(bank_dict['swift_code']),"recipient_name":str(res['recipient_name']),"send_currency":str(res['send_currency']),"receive_currency":str(res['receive_currency']),"receive_amount":str(res['receive_amount']),"exchange_rate":str(res['exchange_rate']),"custmoer_name":str(cus_name['First_name']+ ' ' +cus_name['Last_name']),"sender_address":customer_add,"recipient":recipient_detail,"transactions":str(k)})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))


class PaymentConfirmOtpView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        mobile = request.data.get('mobile')
        code = request.data.get('otp')
        if not mobile:
            return bad_response(message= "Please enter mobile")
        if not code:
            return bad_response(message="Please enter OTP") 
       
        if not User.objects.filter(mobile=mobile).exists():
            return bad_response(message= "Inavlid mobile")
        
        if not User.objects.filter(mobile=mobile, otp=code).exists():
            return bad_response(message="Invalid OTP")
        created_time = User.objects.filter(mobile=mobile, otp=code).values('updated_at')
        token_created_at = created_time[0]['updated_at']
        expire_time = token_created_at + settings.MOBILE_VERIFICATION_TOKEN_EXPIRED
        is_token_expired =  expire_time < timezone.now()
        if is_token_expired == True:
            return bad_response(message="OTP expired") 
        # User.objects.filter(mobile=mobile).update(otp=None)
        return Response({"code":"200","message":"Confirm OTP"})


class Payment_Receipt_download_View(APIView):
    renderer_classes=[UserRenderer]

    @csrf_exempt
    def get(self, request, pk, format=None):
        try:
            context = {}
            id = pk
            if Transaction_details.objects.filter(id=id).exists():
                data = Transaction_details.objects.filter(id=id).values('transaction_id','recipient_name','send_currency', 'receive_currency','amount', 'receive_amount','date', 'reason', 'exchange_rate', 'recipient','customer_id')
                date = str(data[0]['date'])
                date = date.replace("-","/")
                context = {'data': data[0]}
                context.update(date=date)
                if User.objects.filter(customer_id=data[0]['customer_id']).exists():
                    customer_name = User.objects.filter(customer_id=data[0]['customer_id']).values('First_name','Last_name','id')
                    user_id = customer_name[0]['id']
                    customer_name = str(str(customer_name[0]['First_name'])+" "+str(customer_name[0]['Last_name']))
                    context.update(customer_name = customer_name)
                    if User_address.objects.filter(user_id=int(user_id)).exists():
                        a = User_address.objects.filter(user_id=int(user_id)).values('building','street','city','state','country')
                        customer_address = str(str(a[0]['building'])+" "+str(a[0]['street'])+" "+str(a[0]['city'])+" "+str(a[0]['state'])+" "+str(a[0]['country']))
                        context.update(customer_address = customer_address)
                if Recipient.objects.filter(id=data[0]['recipient']).exists():
                    r = Recipient.objects.filter(id=data[0]['recipient']).values('mobile','building','street','city','state','country')
                    recipient_address = str(str(r[0]['building'])+" "+str(r[0]['street'])+" "+str(r[0]['city'])+" "+str(r[0]['state'])+" "+str(r[0]['country']))
                    recipient_mobile = r[0]['mobile']
                    context.update(recipient_mobile=recipient_mobile,recipient_address = recipient_address)
                if Recipient_bank_details.objects.filter(recipient_id=data[0]['recipient']).exists():
                    b = Recipient_bank_details.objects.filter(recipient_id=data[0]['recipient']).values('account_number','account_name','bank_name','swift_code')
                    account_number = b[0]['account_number']
                    swift_code   = b[0]['swift_code']
                    context.update(account_number=account_number, swift_code=swift_code)
            # Render the HTML template with context
            template = get_template('mobile_receipt.html')
            html = template.render(context)
            # Generate a PDF file from the HTML content
            css = CSS(string='@page { size: A4; margin: 1cm }')
            pdf_file = HTML(string=html).write_pdf(stylesheets=[css])
            # Create an HTTP response with the PDF file as content, to prompt the user to download the file
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="receipt.pdf"'
            return response
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))


class Recipient_list_View(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]   
     
    def post(self,request,format=None):
        try:
            serializer = User_Profile_Serializer(request.user)
            if not Recipient.objects.filter(user=serializer.data['id']).exists():
                return success_response(message= "Recipient not found",data=[])
            recipient_data = Recipient.objects.filter(user =serializer.data['id'])
            recipient_serializer = Recipient_List_Serializer(recipient_data, many=True)
            list_array = []
            for i in recipient_serializer.data:
                item = dict(i)
                if Recipient_bank_details.objects.filter(recipient_id=i['id']).exists():
                    bank_data = Recipient_bank_details.objects.filter(recipient_id=i['id']).values('bank_name','account_name','account_number', 'swift_code','bank_address','recipient_id')
                    bank_serializer = Recipient_bank_detail_Serializer(bank_data, many=True)
                    item.update(bank_serializer.data[0])
                list_array.append(item) 
            list_array = sorted(list_array, key=lambda x: x.get('id', 0), reverse=True)

            for x in list_array:
                for key in x:
                        if x[key] is None:
                            x[key] = "" 
                        x[key] = str(x[key]) 
            return success_response(message="success", data=list_array)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))


""" Create recipient """
class Recipient_create_new_View(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]  

    def post(self,request,format=None):
        email = request.data.get("email")
        middle_name = request.data.get("middle_name")
        flat = request.data.get("flat")
        postcode = request.data.get("postcode")
        
        try:
            payload = request.data
            user_id = request.user.id

            RECIPIENT_FIELDS = ['first_name','last_name','mobile','building','street','city','state','country','country_code','bank_name','account_number']
            #validation
            for k in RECIPIENT_FIELDS:
                if not k in payload or str(k).strip() == '' or k == None:
                    return bad_response("Please enter "+replace_(k))

            #creating account name
            account_name = str(payload['first_name'])+" "+str(payload['last_name'])
            
            #concatinating + in mobile if not
            # if 'mobile' in payload:
            #     payload['mobile'] = "+"+str(payload['mobile'])

            # #email and mobile validation
            # if 'email' in payload:
            #     if is_obj_exists(Recipient, {'user_id':user_id, 'email':payload['email']}):
            #         return bad_response("Recipient with this email already exists!")
            # if 'mobile' in payload:
            #     if is_obj_exists(Recipient, {'user_id':user_id, 'mobile':payload['mobile']}):
            #         return bad_response(message="Recipient with this mobile number already exists!")

            #account number validation  
            recipient_users = Recipient.objects.filter(user_id=user_id).values('id')
            if is_obj_exists(Recipient_bank_details, {'recipient_id__in':recipient_users, 'account_number':payload['account_number']}):
                return bad_response('Recipient with this account number already exists')            
           
            create_recipient_dict = {'user_id':user_id,'first_name':payload['first_name'], 'middle_name':middle_name, 'last_name': payload['last_name'], 'email':email, 'mobile':payload['mobile'], 'flat':flat, 'building':payload['building'], 'street':payload['street'], 'city':payload['city'], 'state':payload['state'], 'country':payload['country'], 'country_code':payload['country_code'], 'postcode':postcode}
            if 'address' in payload:
                create_recipient_dict.update(address=payload['address'])
            recipient_data = create_model_obj(Recipient, create_recipient_dict)

            #get recipient data
            serializer = Recipient_list_Serializer(recipient_data)
            data = dict(serializer.data)

            #creating recipient bank details
            bank_dict = {'recipient_id':serializer.data['id'],'bank_name':payload['bank_name'],'account_name':account_name,'account_number':payload['account_number']}
            bank_data = create_model_obj(Recipient_bank_details, bank_dict)           
            data.update(bank_dict)
            return success_response("success", data_to_str([data])[0])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in mobile_payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))   


"""Old api"""
class Recipient_create_View(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]  

    def post(self,request,format=None):
        email= None
        first_name     = request.data.get("first_name")
        middle_name    = request.data.get("middle_name")
        last_name      = request.data.get("last_name")
        email          = request.data.get("email")
        mobile         = request.data.get("mobile")
        flat           = request.data.get("flat")
        building       = request.data.get("building")
        street         = request.data.get("street")
        postcode       = request.data.get("postcode")
        city           = request.data.get("city")
        state          = request.data.get("state")
        country        = request.data.get("country")
        bank_name      = request.data.get("bank_name")
        swift_code     = request.data.get("swift_code")
        bank_address   = request.data.get("bank_address")
        account_number = request.data.get("account_number")
        country_code   = request.data.get("country_code")
        
        try:
            user_serializer = User_Profile_Serializer(request.user)
            user_id = user_serializer.data['id']

            f_name = request.data.get("first_name")
            f  = f_name.replace(" ", "")
            # print("===",f)
            m_name = request.data.get("middle_name")
            m  = m_name.replace(" ", "")

            l_name = request.data.get("last_name")
            l  = l_name.replace(" ", "")

            # mobile= mobile.replace("+", "")
            # checking values
            error_dict = {'bank_name':bank_name,'bank address':bank_address,'account number':account_number,'first_name':first_name, 'last_name': last_name,'mobile':mobile}
            for k, v in zip(error_dict.keys(), error_dict.values()):       
                if not v:
                    key = k.replace("_"," ")
                    return bad_response(message="Please enter "+key)
                
            if email == None:
                return bad_response(message="Please enter email.")
            if Recipient.objects.filter(user=user_serializer.data['id'], mobile=mobile).exists():
                return bad_response(message="Recipient with this mobile number already exists!")     
            # if Recipient.objects.filter(user=user_serializer.data['id'], email=email).exists():
            #     return bad_response(message="Recipient with this email already exists!")
            account_name = str(first_name)+ " "+str(last_name)
            recipient_users = Recipient.objects.filter(user=user_id).values('id')
            for x in recipient_users:
                if account_number and Recipient_bank_details.objects.filter(recipient_id=x['id'], account_number=account_number).exists():
                    return bad_response(message='Recipient with this account number already exists')
            recipient_dict = {'first_name':f, 'middle_name':m, 'last_name': l, 'email':email, 'mobile':mobile, 'flat':flat, 'building':building, 'street':street, 'city':city, 'state':state, 'country':country, 'country_code':country_code}
            filtered_dict = {k: v for k, v in recipient_dict.items() if v != None }
            filtered_dict.update(user_id=user_id)
            if postcode:
                filtered_dict.update(postcode=postcode)
            recipient_data = Recipient.objects.create(**filtered_dict)
            recipient_serializer = Recipient_List_Serializer(recipient_data)
            bank_data = Recipient_bank_details.objects.create(recipient_id=recipient_serializer.data['id'], bank_name=bank_name, swift_code=swift_code, bank_address=bank_address, account_number=account_number,account_name=account_name)
            bank_serializer = Recipient_bank_detail_Serializer(bank_data)
            dict = recipient_serializer.data.copy()
            dict.update(bank_serializer.data)
            # del dict['recipient_id']
            # dict['id'] = dict['recipient_id'] 
            # del dict['recipient_id']    
            for key in dict:
                if dict[key] is None:
                    dict[key] = "" 
                dict[key] = str(dict[key]) 
            return success_response(message="success", data=dict)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))


class Recipient_update_new_View(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]    

    @csrf_exempt
    def get(self, request, pk, format=None):
        try:
            if not Recipient.objects.filter(id=pk).exists():
                return bad_response(message="Recipient does not exist")
            recipient =  Recipient.objects.get(pk=pk)
            serializer = Recipient_List_Serializer(recipient)
            bank = Recipient_bank_details.objects.filter(recipient=serializer.data['id']).values('bank_name','account_name','account_number','bank_address')
            dict = serializer.data.copy()
            dict.update(bank[0])
            for key in dict:
                if dict[key] is None:
                    dict[key] = "" 
                dict[key] = str(dict[key]) 
            return success_response(message="success", data=dict)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))


    @csrf_exempt
    def post(self, request, pk, format=None):
        user_profile = User_Profile_Serializer(request.user)
        user_id = int(user_profile.data['id'])
        if not Recipient.objects.filter(user=user_id, id=pk).exists():
            return bad_response(message="No recipient found for this user")   
        first_name     = request.data.get("first_name")
        middle_name    = request.data.get("middle_name")
        last_name      = request.data.get("last_name")
        email          = request.data.get("email")
        mobile         = request.data.get("mobile")
        flat           = request.data.get("flat")
        building       = request.data.get("building")
        street         = request.data.get("street")
        postcode       = request.data.get("postcode")
        city           = request.data.get("city")
        state          = request.data.get("state")
        country        = request.data.get("country")
        bank_name      = request.data.get("bank_name")
        # account_name   = request.data.get("account_name")
        account_number = request.data.get("account_number")
        try:

            f_name = request.data.get("first_name")
            f  = f_name.replace(" ", "")
           
            m_name = request.data.get("middle_name")
            m  = m_name.replace(" ", "")

            l_name = request.data.get("last_name")
            l  = l_name.replace(" ", "")
            account_name = str(f)+ " "+str(l)
            print("accccc",account_name)
            error_dict = {'bank_name':bank_name,'account name':account_name, 'account number':account_number,'first_name':f,'last_name': l, 'email':email, 'mobile':mobile}
            for k, v in zip(error_dict.keys(), error_dict.values()):
                if v == "" or v == " ":
                    key = k.replace("_"," ")
                    return bad_response(message="Please enter "+key)    
            # updating recipient data
            dict = {'first_name':f, 'middle_name': m, 'last_name': l, 'email':email, 'mobile':mobile, 'flat':flat, 'building':building, 'street':street, 'city':city, 'state':state, 'country':country}
            filtered_dict = {k: v for k, v in dict.items() if v is not None}
            dict.clear()
            dict.update(filtered_dict)
            if postcode is not None:
                filtered_dict.update(postcode=postcode)
            recipient_data = Recipient.objects.filter(id=pk).update(**filtered_dict)
            #updating recipient bank data
            bank_dict = {'bank_name':bank_name, 'account_name':account_name, 'account_number':account_number}
            filtered_bank_dict = {k: v for k, v in bank_dict.items() if v is not None}
            bank_dict.clear()
            bank_dict.update(filtered_bank_dict)
            Recipient_bank_details.objects.filter(recipient_id=pk).update(**filtered_bank_dict)
            # getting data for response
            recipient =  Recipient.objects.get(pk=pk)
            recipientserializer = Recipient_List_Serializer(recipient)
            bank_data = Recipient_bank_details.objects.get(recipient_id=pk)
            bankserializer = Recipient_bank_details_Serializer(bank_data)
            data_dict = recipientserializer.data.copy()
            data_dict.update(bankserializer.data)
            for key in data_dict:
                if data_dict[key] is None:
                    data_dict[key] = "" 
                data_dict[key] = str(data_dict[key]) 
            return success_response(message="success", data= data_dict)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))


    @csrf_exempt
    def delete(self, request, pk, format=None):
        try:
            if not Recipient.objects.filter(id=pk).exists():
                return bad_response(message="Recipient does not exist")
            recipient =  Recipient.objects.get(pk=pk)
            bank = Recipient_bank_details.objects.filter(recipient_id=pk)
            if recipient.delete() and bank.delete():
                return success_response(message="Recipient deleted successfully", data=None)
            return bad_response(message="Recipient is not deleted")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))



"""Old api"""
class Recipient_update_View(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]    

    @csrf_exempt
    def get(self, request, pk, format=None):
        try:
            if not Recipient.objects.filter(id=pk).exists():
                return bad_response(message="Recipient does not exist")
            recipient =  Recipient.objects.get(pk=pk)
            serializer = Recipient_List_Serializer(recipient)
            bank = Recipient_bank_details.objects.filter(recipient=serializer.data['id']).values('bank_name','account_name','swift_code','account_number','bank_address')
            dict = serializer.data.copy()
            dict.update(bank[0])
            for key in dict:
                if dict[key] is None:
                    dict[key] = "" 
                dict[key] = str(dict[key]) 
            return success_response(message="success", data=dict)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))


    @csrf_exempt
    def post(self, request, pk, format=None):
        user_profile = User_Profile_Serializer(request.user)
        user_id = int(user_profile.data['id'])
        if not Recipient.objects.filter(user=user_id, id=pk).exists():
            return bad_response(message="No recipient found for this user")   
        first_name     = request.data.get("first_name")
        middle_name    = request.data.get("middle_name")
        last_name      = request.data.get("last_name")
        email          = request.data.get("email")
        mobile         = request.data.get("mobile")
        flat           = request.data.get("flat")
        building       = request.data.get("building")
        street         = request.data.get("street")
        postcode       = request.data.get("postcode")
        city           = request.data.get("city")
        state          = request.data.get("state")
        country        = request.data.get("country")
        bank_name      = request.data.get("bank_name")
        # account_name   = request.data.get("account_name")
        account_number = request.data.get("account_number")
        try:

            f_name = request.data.get("first_name")
            f  = f_name.replace(" ", "")
           
            m_name = request.data.get("middle_name")
            m  = m_name.replace(" ", "")

            l_name = request.data.get("last_name")
            l  = l_name.replace(" ", "")
            account_name = str(f)+ " "+str(l)
            print("accccc",account_name)
            error_dict = {'bank_name':bank_name,'account name':account_name, 'account number':account_number,'first_name':f,'last_name': l, 'email':email, 'mobile':mobile}
            for k, v in zip(error_dict.keys(), error_dict.values()):
                if v == "" or v == " ":
                    key = k.replace("_"," ")
                    return bad_response(message="Please enter "+key)    
            # updating recipient data
            dict = {'first_name':f, 'middle_name': m, 'last_name': l, 'email':email, 'mobile':mobile, 'flat':flat, 'building':building, 'street':street, 'city':city, 'state':state, 'country':country}
            filtered_dict = {k: v for k, v in dict.items() if v is not None}
            dict.clear()
            dict.update(filtered_dict)
            if postcode is not None:
                filtered_dict.update(postcode=postcode)
            recipient_data = Recipient.objects.filter(id=pk).update(**filtered_dict)
            #updating recipient bank data
            bank_dict = {'bank_name':bank_name, 'account_name':account_name, 'account_number':account_number}
            filtered_bank_dict = {k: v for k, v in bank_dict.items() if v is not None}
            bank_dict.clear()
            bank_dict.update(filtered_bank_dict)
            Recipient_bank_details.objects.filter(recipient_id=pk).update(**filtered_bank_dict)
            # getting data for response
            recipient =  Recipient.objects.get(pk=pk)
            recipientserializer = Recipient_List_Serializer(recipient)
            bank_data = Recipient_bank_details.objects.get(recipient_id=pk)
            bankserializer = Recipient_bank_details_Serializer(bank_data)
            data_dict = recipientserializer.data.copy()
            data_dict.update(bankserializer.data)
            for key in data_dict:
                if data_dict[key] is None:
                    data_dict[key] = "" 
                data_dict[key] = str(data_dict[key]) 
            return success_response(message="success", data= data_dict)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))


    @csrf_exempt
    def delete(self, request, pk, format=None):
        try:
            if not Recipient.objects.filter(id=pk).exists():
                return bad_response(message="Recipient does not exist")
            recipient =  Recipient.objects.get(pk=pk)
            bank = Recipient_bank_details.objects.filter(recipient_id=pk)
            if recipient.delete() and bank.delete():
                return success_response(message="Recipient deleted successfully", data=None)
            return bad_response(message="Recipient is not deleted")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))



import ast
class transaction_history(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]  

    def post(self, request, format=None):
        type = request.data.get('type')
        user = User_Profile_Serializer(request.user)
        recipient = request.data.get('recipient')
        customer_id = user.data['customer_id']
        if not User.objects.filter(customer_id=customer_id, is_superuser=False).exists():
            return bad_response(message="User doest not exist")
        if not Transaction_details.objects.filter(customer_id=customer_id).exists():
            return bad_response(message="You have not created any transaction yet")
        if recipient:
            queryset = Transaction_details.objects.filter(Q(customer_id = customer_id) & Q(recipient=recipient)).values('id', 'recipient','exchange_rate', 'date', 'tm_label','transaction_id','card_type','recipient_name','customer_id','recipient','send_currency','receive_currency','amount','send_method', 'receive_amount','receive_method', 'payment_status', 'payment_status_reason','tm_status','reason','created_at', 'risk_score','risk_group').order_by('-id')
            data = []
        else:
            queryset = Transaction_details.objects.filter(customer_id = customer_id).values('id', 'recipient','exchange_rate', 'date', 'tm_label','transaction_id','card_type','recipient_name','customer_id','recipient','send_currency','receive_currency','amount','send_method', 'receive_amount','receive_method', 'payment_status', 'payment_status_reason','tm_status','reason','created_at', 'risk_score','risk_group').order_by('-id')
        data = []
        rec_data = []
        bank_data = []
        for i in queryset:
            if i['recipient']:
                if str(i['payment_status']) != str(transaction['incomplete']):
                    data.append(i)
                    p = i['recipient']
                    if not p:
                        res = ""
                    else:
                        res = Recipient.objects.filter(id=p).values('id','first_name','last_name','email','mobile','flat','building','street','city','state','country')[0]
                        rec_data.append(res)
                        sa = Recipient_bank_details.objects.filter(recipient_id=p).values('recipient_id','account_number','swift_code')[0]
                        bank_data.append(sa)
                
        if user.data['Middle_name']:
            customer_name = str(user.data['First_name'])+" "+str(user.data['Middle_name'])+" "+str(user.data['Last_name'])
        else:
            customer_name = str(user.data['First_name'])+" "+str(user.data['Last_name'])

        if HOST == "LOCAL":
            val = settings.BASE_URL+"/mobile_payment/receipt/"
        if HOST == "TEST":
            val = settings.BASE_URL+"/mobile_payment/receipt/"
        if HOST == "LIVE":
            val = settings.BASE_URL+"/mobile_payment/receipt/"
        # val="https://api.remitassure.com/mobile_payment/receipt/"
        for i in range(len(data)):
            data[i]["receipt url"]=val+str(data[i]["id"])

        add = User_address.objects.filter(user_id=request.user.id).values('flat','building','street','city','postcode','state','country','country_code')
        customer_add = add[0]

         #for get custmoer_name
        us = User.objects.filter(id=request.user.id).values('First_name', 'Last_name')
        cus_name = us[0]

        for i in data:
            r_id = i['recipient']
            for j in rec_data:
                r2_id = j['id']
                if int(r2_id) == int(r_id):
                    i['recipient'] = j
                    break


        for i in data:
            b_id = i['recipient']['id']
            for v in bank_data:
                b2_id = v['recipient_id']
                if int(b2_id) == int(b_id):
                    i['bank_details'] = v
                    break

        for x in data:
            # print(data , "x ======")
            for key in x:
                if x[key] is None:
                    x[key] = "" 
                x[key] = str(x[key]) 
            x["customer_name"]=str(cus_name['First_name']+ ' ' +cus_name['Last_name'])
            x["sender_address"]=customer_add
            # if not x['recipient']:
            #     x['recipient'] = None
            # else:
            x['recipient'] =  ast.literal_eval(x['recipient'])
            # bank_details = x.get('bank_details', "")

            # if not bank_details:
            #     x['bank_details'] = None
            # else:
            x['bank_details'] = ast.literal_eval(x['bank_details'])

        
        return JsonResponse({'code':"200", 'message':"success", 'data':data})

"""V1 api"""        
class transaction_history_v1(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]  

    def post(self, request, format=None):
        type = request.data.get('type')
        customer_id = request.user.customer_id
        if not is_obj_exists(User, {'customer_id':customer_id, 'is_superuser':False}):
            return bad_response("User doest not exists!")
        if not is_obj_exists(Transaction_details, {'customer_id':customer_id}):
            return bad_response("You have not created any transaction yet")
        queryset = list(Transaction_details.objects.filter(customer_id=customer_id).exclude(payment_status__iexact=str(transaction['incomplete'])).values('id', 'recipient','exchange_rate', 'date', 'tm_label','transaction_id','card_type','recipient_name','customer_id','recipient','send_currency','receive_currency','amount','send_method', 'receive_amount','receive_method', 'payment_status', 'payment_status_reason','tm_status','reason','updated_at', 'risk_score','risk_group','total_amount','discount_amount').order_by('-id'))
        total_amount = Transaction_details.objects.filter(customer_id = customer_id).exclude(payment_status__iexact=str(transaction['incomplete'])).aggregate(total=Sum('total_amount'))
        final_amount = Transaction_details.objects.filter(customer_id = customer_id).exclude(payment_status__iexact=str(transaction['incomplete'])).aggregate(total=Sum('amount'))
        discount_amount = Transaction_details.objects.filter(customer_id = customer_id).exclude(payment_status__iexact=str(transaction['incomplete'])).aggregate(total=Sum('discount_amount'))
        if request.user.Middle_name:
            customer_name = str(request.user.First_name)+" "+str(request.user.Middle_name)+" "+str(request.user.Last_name)
        else:
            customer_name = str(request.user.First_name)+" "+str(request.user.Last_name)
        for x in queryset:
            x['total_amount'] = comma_value(x['total_amount'])
            x['receive_amount'] = comma_value(x['receive_amount'])
            x['amount'] = comma_value(x['amount'])
            for key in x:
                if x[key] is None:
                    x[key] = "" 
                x[key] = str(x[key]) 
        return success_response("success", {'total_amount':comma_value(total_amount['total']), 'final_amount':comma_value(final_amount['total']),'discount_amount':comma_value(discount_amount['total']), 'transaction_list':queryset})


# for user dashboard after login
class Stripe_Payment_View(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None): 
        card_token       = request.data.get('card_token')
        send_currency    = request.data.get('send_currency')
        receive_currency = request.data.get('receive_currency')
        destination      = request.data.get('destination')
        recipient_id     = request.data.get('recipient_id')
        send_amount      = request.data.get('send_amount')    
        receive_amount   = request.data.get('receive_amount') 
        exchange_rate    = request.data.get('exchange_rate')
        reason           = request.data.get('reason')
        profile_serializer = User_Profile_Serializer(request.user)

        try:
            #checking empty values 
            data_dict = {'card_token':card_token, 'send_currency':send_currency, 'receive_currency':receive_currency, 'send_amount':send_amount, 'receive_amount':receive_amount, 'reason':reason, 'recipient_id':recipient_id, 'exchange_rate':exchange_rate} 
            for k, v in zip(data_dict.keys(), data_dict.values()):
                data_dict[k] == str(data_dict[k])
                key = k.replace("_"," ")
                if v is None or v == "":
                    return bad_response(message='Please enter '+key)
            if not Recipient.objects.filter(user_id=profile_serializer.data['id'], id= recipient_id).exists():
                return bad_response(message="Invalid recipient id")

            #retrieving card details with card token
            try:
                card_data = stripe.Token.retrieve(card_token)
                card_last4_digits = card_data['card']['last4']
                card_type_key = card_data['card']['brand']
                card_id = card_data['card']['id']
                exp_date = str(card_data['card']['exp_month'])+"-"+str(card_data['card']['exp_year'])
                fingerprint = str(card_data['card']['fingerprint'])
            except stripe.error.StripeError as e:
                return bad_response(message= e.user_message)
            
            # card type values for fraud.net 
            card_dict = {'Visa': "visa", 'Mastercard':"mc", 'American Express':"amex", 'Discover':"discover", 'Diners Club':"diners_club"}
            if card_type_key in card_dict:
                card_type = card_dict[card_type_key]
            else:
                card_type = "other"

            # creating and retrieving stripe customer
            if profile_serializer.data['stripe_customer_id']:
                stripe_customer_id = profile_serializer.data['stripe_customer_id']
            else:
                stripe_customer_id = None
            try:
                search = stripe.Customer.retrieve(stripe_customer_id)
            except stripe.error.StripeError as e:
                try:
                    customer_data = stripe.Customer.create(name= profile_serializer.data['First_name']+" "+profile_serializer.data['Last_name'], email=profile_serializer.data['email'])
                    stripe_customer_id = customer_data['id'] 
                    User.objects.filter(email=profile_serializer.data['email'],is_superuser=False).update(stripe_customer_id=stripe_customer_id)
                except stripe.error.StripeError as e:
                    return bad_response(message=e.user_message)

            #fetching recipient name details
            recipient_data =  Recipient.objects.filter(id=recipient_id).values('first_name','last_name','middle_name','email','mobile','flat','building','street','city','state', 'postcode','country_code','country')
            recipient_name = recipient_data[0]['first_name'] + " "+recipient_data[0]['last_name']
            recipient = recipient_data[0]
            send_currency = str(send_currency).upper()
            if '.' in send_amount:
                send_amount = round(float(send_amount))
            else:
                send_amount = int(send_amount)
            stripe_send_amount = send_amount*100
            send_amount = str(send_amount)
            source_data = stripe.Customer.create_source(stripe_customer_id, source = card_token)
           
            #creating stripe charge
            try:
                payment_intent = stripe.Charge.create(
                customer = stripe_customer_id,
                amount= stripe_send_amount,
                currency= send_currency,
                source= card_id,
                metadata= {'name': profile_serializer.data['First_name'] + profile_serializer.data['Last_name'], 'customer_id': profile_serializer.data['customer_id'], 'recipient': recipient_name}, 
                description= reason
                )         
            except stripe.error.StripeError as e:
                return bad_response(message=e.user_message)
            
            charge_id = payment_intent['id']
            status = payment_intent['status']
            payment_status = transaction['pending_review']
            fraudnet_payment_status = None
            if 'status' in payment_intent:
                if status == "succeeded":
                    fraudnet_payment_status = "approved"         
                else:
                    fraudnet_payment_status = "cancelled"  
            transaction_data = Transaction_details.objects.create(payment_gateway_transaction_id = charge_id, exchange_rate=str(exchange_rate),card_type=card_type,recipient_name=recipient_name, customer_id=profile_serializer.data['customer_id'], recipient=recipient_id, send_currency=send_currency, receive_currency= receive_currency, amount= send_amount, receive_amount = receive_amount, send_method= card_type+" card", payment_status= payment_status, reason=reason, card_token= card_token)
            k=0
            val = User.objects.filter(id=request.user.id).values('transactions')
            # print("=====",val[0]["transactions"])
            if val[0]["transactions"]:
                k=int(val[0]["transactions"])
                k=k+1
                User.objects.filter(id=request.user.id).update(transactions=k)
            else:
                k=1
                User.objects.filter(id=request.user.id).update(transactions=k)
            transaction_id = str(getattr(transaction_data, 'id'))  
            tid = str(getattr(transaction_data, 'id'))  
            payment_id = create_payment_id(transaction_id=transaction_id)
            created_at = str(getattr(transaction_data, 'created_at'))
            # print("!!!!!!!",created_at)  
            v_datetime = datetime.strptime(str(created_at), '%Y-%m-%d %H:%M:%S.%f')
            date_part = v_datetime.date()
            date_val = date_part.strftime('%Y-%m-%d')
            notification.objects.create(source_id=tid, source_type="transaction", source_detail=str(send_amount)+" "+str(send_currency), message=settings.NOTIFICATION_TRANSACTION_MSG)
            t_obj = Transaction_details.objects.filter(id=tid)
            send_sms_to_RA(type="transaction",data={'transaction_id':payment_id,'customer_id':profile_serializer.data['customer_id'],'send_currency':send_currency, 'amount': send_amount, 'exchange_rate':exchange_rate})
            # email_to_RA(type="transaction", data={'send_method':"Stripe",'transaction_id':payment_id,'customer_name':str(profile_serializer.data['First_name'])+" "+str(profile_serializer.data['Last_name']), 'email':profile_serializer.data['email'],'customer_id':profile_serializer.data['customer_id'],'send_currency':send_currency, 'amount': send_amount, 'exchange_rate':exchange_rate, 'receive_currency':t_obj[0].receive_currency, 'receive_amount':t_obj[0].receive_amount})
            email_to_RA(type="transaction", id = transaction_id)

            #for pdf url
            s = str(transaction_id)
            val="https://api.remitassure.com/mobile_payment/receipt/"
            # val="http://127.0.0.1:8000/mobile_payment/receipt/"
            url=val+s

            #getting bank details 
            bank_data = Recipient_bank_details.objects.filter(recipient_id=recipient_id).values('account_number','bank_name','account_name','swift_code','bank_address')   
            bank_list = list(bank_data)
            bank_dict = bank_list[0]

            #GETTING SENDER ADDRES FROM USER ADDRESS TABLE
            sender_address = User_address.objects.filter(user_id=profile_serializer.data['id']).values('flat','building','street','postcode','city','state','country_code','country')
            sender_address = sender_address[0]
            recipient_country_code = str(recipient['country_code']).upper()
            fn                     = str(profile_serializer.data['First_name'])
            ln                     = str(profile_serializer.data['Last_name'])
            city                   = str(sender_address['city'])
            state                  = str(sender_address['state'])
            sender_country_code    = str(sender_address['country_code']).upper()
            dob                    = str(profile_serializer.data['Date_of_birth'])
            mobile                 = str(profile_serializer.data['mobile'])
            email                  = str(profile_serializer.data['email'])
            postcode               = str(sender_address['postcode'])
            account_no             = str(bank_data[0]['account_number'])
            receivecurrency        = str(receive_currency).upper()
            user_id                = str(profile_serializer.data['customer_id'])
            transaction_data       = Transaction_details.objects.filter(id=transaction_id).update( transaction_id=payment_id)
            address1 = sender_address['building']+" "+sender_address['street']
            address1 = str(address1)
            seller_address = str(recipient['building']+" "+recipient['street']+" "+recipient['city']+" "+recipient['state'])
            seller_name = recipient_name
            customer_id=user_id
            customer_country_code = sender_country_code
            recipient_address = seller_address
            address = str(address1)
            response = fraudnet_check_transaction(fingerprint, customer_id, fn, ln, address, city, state, postcode,customer_country_code, dob, mobile, email, recipient_id, recipient_country_code, recipient_address, recipient_name, account_no, exp_date, card_last4_digits, payment_id, card_type, send_currency, send_amount, receivecurrency, fraudnet_payment_status, transaction_id)
            if 'source' in response:
                if response['source'] == "Duplicate Order":
                    transaction_id = str(date.today())+"0"+tid
                    response = fraudnet_check_transaction(fingerprint, customer_id, fn, ln, address, city, state, postcode,customer_country_code, dob, mobile, email, recipient_id, recipient_country_code, recipient_address, recipient_name, account_no, exp_date, card_last4_digits, payment_id, card_type, send_currency, send_amount, receivecurrency, fraudnet_payment_status, transaction_id)
            if 'data' in response:
                payment_status = update_fn_data_in_db(response=response, customer_id=customer_id, transaction_id=transaction_id)
                tm_status = Transaction_details.objects.filter(id=transaction_id).values('tm_status')
                tm_status = tm_status[0]['tm_status']
                if tm_status == "approved":
                    payment_status = transaction['pending_review']
                elif tm_status == "queued":
                    payment_status = "Compliance Review"
                elif tm_status == "cancelled":
                    payment_status = "Cancelled"
                else:
                    payment_status = tm_status
                Transaction_details.objects.filter(id=transaction_id).update(payment_status=payment_status)
            return success_response(message=payment_status, data={"id":str(transaction_id),"payment_id":str(payment_id),"url":str(url),"status":payment_status,"date":str(date_val),"transactions":str(k),"customer_name":fn+ ' '+ln,"exchange_rate":str(exchange_rate),"send_currency":str(send_currency),"receive_currency":str(receive_currency),"send_amount":str(send_amount),"receive_amount":str(receive_amount),"account_name":str(bank_dict['account_number']),"swift_code":str(bank_dict['swift_code']),"sender_address":sender_address,"recipient":recipient})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))



class stripe_create_card_view(APIView):
    renderer_classes=[UserRenderer]
    
    def post(self, request, format=None):
        name = request.data.get('name')
        card_number = request.data.get('card_number')
        expiry_month = request.data.get('expiry_month')
        expiry_year = request.data.get('expiry_year')
        try:
            error_dict = {'card_number':card_number, 'expiry_month':expiry_month, 'expiry_year':expiry_year}
            for k, v in zip(error_dict.keys(), error_dict.values()):
                if not v or v == "":
                    key = k.replace("_"," ")
                    return bad_response(message="Please enter "+key)
            try:
                card_data = stripe.Token.create(
                card={
                        "number": card_number,
                        "exp_month": expiry_month,
                        "exp_year": expiry_year,
                    }, )
                card_token = card_data['id']
                card_id = card_data['card']['id']
                pass
                return success_response(message="success", data={'card_token':card_token, 'card_id':card_id})
            except stripe.error.CardError as error:
                return bad_response(message=error.user_message) 
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))


class SearchViewSet(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        recipient_data=request.query_params.get("search")
        print(request.user.id)

        if recipient_data:
            queryset = Recipient.objects.filter(user=request.user.id,first_name__icontains=recipient_data)
        else:
            queryset = Recipient.objects.filter(user=request.user.id)
        return success_response(message="success", data={'transaction':queryset.values()})



class Stripe_old_Payment_ViewSet(viewsets.ViewSet):
    @csrf_exempt 
    @action(detail=False, permission_classes=[IsAuthenticated], methods=['POST'])        
    def stripe_card(self, request, format=None):
        name         = request.data.get('name') 
        card_number  = request.data.get('card_number')
        expiry_month = request.data.get('expiry_month')
        expiry_year  = request.data.get('expiry_year')
        cvc          = request.data.get('cvc')
        card_token   = request.data.get('card_token')
        save_card    = request.data.get('save_card')
        type         = request.data.get('type')
        user_serializer = User_Profile_Serializer(request.user)
        db_card_id = None
        # checking that card token exist or not
        if card_token and not stripe_card_details.objects.filter(card_token=card_token, customer_id=user_serializer.data['customer_id']).exists():
            raise serializers.ValidationError({"code": settings.BAD_REQUEST, 'message': 'Invalid card token', 'card_token':'Invalid card token' })
        #if card exist then fetching card details
        if card_token and stripe_card_details.objects.filter(card_token=card_token, customer_id=user_serializer.data['customer_id']).exists():
            card_token_data = stripe_card_details.objects.filter(card_token=card_token, customer_id=user_serializer.data['customer_id']).values('id','card_token','card_id','name','card_number','expiry_month','expiry_year')
            name = card_token_data[0]['name']
            card_number = card_token_data[0]['card_number']
            expiry_month = card_token_data[0]['expiry_month']
            expiry_year = card_token_data[0]['expiry_year']
            db_card_id = card_token_data[0]['id']
        #checking empty values 
        data_dict = {'name':name,'card_number':card_number,'expiry_month':expiry_month,'expiry_year':expiry_year,'cvc':cvc} 
        for k, v in zip(data_dict.keys(), data_dict.values()):
            data_dict[k] == str(data_dict[k])
            key = k.replace("_"," ")
            if v is None or v == "":
                raise serializers.ValidationError({"code": settings.BAD_REQUEST, 'message': 'Please enter '+key, k:'Please enter '+key })
        #checking card credentials and creating card token to create payment
        try:
            token_data = stripe.Token.create(
            card={
                "name":name,
                "number": card_number,
                "exp_month": expiry_month,
                "exp_year": expiry_year,
                "cvc": cvc,
            }, )
            card_token = token_data['id']
            card_id = token_data['card']['id']
            retrieve_card_data = stripe.Token.retrieve(card_token)
            card_type = retrieve_card_data['card']['brand']
            pass
        except stripe.error.CardError as error:
            raise serializers.ValidationError({"code":settings.BAD_REQUEST, 'message':str(error.user_message), "error": str(error.user_message)})
        #updating card tokens of existing card
        if db_card_id is not None:
            stripe_card_details.objects.filter(id=db_card_id).update(card_token=card_token, card_id=card_id)
        #saving card if user want to save it
        if save_card == "true" or save_card == "1":
            if not stripe_card_details.objects.filter(customer_id=user_serializer.data['customer_id'], card_number=card_number).exists():
                stripe_card_details.objects.create(customer_id=user_serializer.data['customer_id'], name=name, card_number=card_number, expiry_month=expiry_month, expiry_year=expiry_year, card_id=card_id, card_token=card_token)
        if not card_id:
            raise serializers.ValidationError({"code":settings.BAD_REQUEST, "message":"Card Id is not created. Please try again"})      
        if stripe_card_token.objects.filter(customer_id = user_serializer.data['customer_id']).exists():
            stripe_card_token.objects.filter(customer_id = user_serializer.data['customer_id']).update(name=name, card_id=card_id, card_token=card_token)
        else:    
            stripe_card_token.objects.create(name=name, customer_id = user_serializer.data['customer_id'], card_token=card_token, card_id=card_id)
        stripe_card_details.objects.filter(customer_id=user_serializer.data['customer_id'], card_number=card_number).update(card_id=card_id, card_token=card_token)
        stripe_card_token.objects.filter(customer_id=user_serializer.data['customer_id']).update(card_id=card_id, card_token=card_token)
        if type == None:
            return Response({'code': settings.SUCCESS_CODE, 'message': settings.SUCCESS_MESSAGE, 'card_id':card_token})
        return Response({'code': settings.SUCCESS_CODE, 'message': settings.SUCCESS_MESSAGE, 'data':{'card_id':str(card_id), 'card_token': str(card_token)}})


def payment_usage_check_mobile(user_id, customer_id, transaction_id):
    try:
        status = None
        current_amount = 0
        one_year_ago = timezone.now() - timedelta(days=365)

        if Transaction_details.objects.filter(transaction_id=transaction_id).exists():
            transaction_data = Transaction_details.objects.filter(transaction_id=transaction_id).values('amount')
            current_amount = replace_comma(transaction_data[0]['amount'])

        if User.objects.filter(customer_id=customer_id).exists():
            data = User.objects.filter(customer_id=customer_id).values('value_per_annum','payment_per_annum')
            value_per_annum = data[0]['value_per_annum']
            payment_per_annum = data[0]['payment_per_annum']

            #get transactions count
            transactions_count = Transaction_details.objects.filter(Q(payment_status=transaction['completed']) | Q(payment_status=transaction['pending_review']), customer_id=customer_id, date__gte=one_year_ago).count()
            #get total of amount sent in one year
            transactions = Transaction_details.objects.filter(Q(payment_status=transaction['completed']) | Q(payment_status=transaction['pending_review']), customer_id=customer_id, date__gte=one_year_ago).values('amount')           
            total_amount = sum(float(replace_comma(str(trans['amount']))) for trans in transactions)

            #add current amount in total amount and transaction count for current one
            total_amount = float(total_amount)+float(current_amount)
            transactions_count += 1

            #find values from list
            count_value = next((item[payment_per_annum] for item in PAYMENT_PER_ANNUM_LIST if payment_per_annum in item), None)
            amount_value = next((item[value_per_annum] for item in VALUE_PER_ANNUM_LIST if value_per_annum in item), None)

            #conditions
            if count_value and count_value != 'unlimited' and int(transactions_count) > int(count_value):
                status = "You have reached your transaction limit , please upgrade your tier to continue transaction or try with lesser amount."               
            elif amount_value and amount_value != 'unlimited' and float(total_amount) > float(amount_value):  
                status = "You have reached your transaction limit , please upgrade your tier to continue transaction or try with lesser amount." 
        return status
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return None   



class Create_Update_Transaction_View(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]  

    def post(self,request,format=None):
        transaction_id = request.data.get("transaction_id")
        amount = request.data.get("amount")
        recipient_id = request.data.get("recipient_id")
        app_version = request.data.get('app_version')
        platform = request.data.get('platform')

        
        try:
            user_serializer = User_Profile_Serializer(request.user)
            customer_id = user_serializer.data['customer_id']
            send_method = None
            send_method = amount['send_method']
            is_digital_Id_verified = user_serializer.data['is_digital_Id_verified']
            
               
            if not transaction_id and not amount:
                return bad_response(message="Please enter transaction_id or amount details.")  
            if transaction_id:
                # if is_digital_Id_verified != "approved":
                #     return Response({"code":"401","message":"Your account is logged out because your account is not verified, please log-in into WidophRemit.com website to complete the KYC or reach out to the admin."},status=status.HTTP_401_UNAUTHORIZED)
                if not Transaction_details.objects.filter(transaction_id=transaction_id, customer_id=customer_id).exists():
                    return bad_response(message="Invalid transaction_id")             
                if amount:
                    Transaction_details.objects.filter(transaction_id=transaction_id).update(send_method=send_method, send_currency=str(amount['send_currency']).upper(), amount=str(amount['send_amount']), total_amount=str(amount['send_amount']),payout_partner = str(amount['payout_partner']),receive_amount= str(amount['receive_amount']),receive_method= str(amount['receieve_method']) ,receive_currency=str(amount['receive_currency']).upper(), reason=amount['reason'], exchange_rate=amount['exchange_rate'], updated_at=get_current_datetime())       
                if recipient_id:
                    if Recipient.objects.filter(id=recipient_id).exists():
                        name = Recipient.objects.filter(id=recipient_id).values('first_name','last_name')
                        recipient_name= str(name[0]['first_name'])+" "+str(name[0]['last_name'])
                        Transaction_details.objects.filter(transaction_id=transaction_id).update(recipient_name=recipient_name,recipient=recipient_id,risk_score="NA", risk_group="NA",tm_status="NA", tm_label = "NA", updated_at=get_current_datetime())
            else:
                transaction_data = Transaction_details.objects.create(app_version=app_version,platform=platform,payment_status=transaction['incomplete'], send_method=send_method,payout_partner = str(amount['payout_partner']),recipient=recipient_id,risk_score="NA", risk_group="NA", tm_status="NA", tm_label = "NA",  customer_id=customer_id, send_currency=str(amount['send_currency']).upper(), amount=str(amount['send_amount']), total_amount = str(amount['send_amount']),receive_amount= str(amount['receive_amount']), receive_method= str(amount['receieve_method']),receive_currency=str(amount['receive_currency']).upper(), reason=amount['reason'], exchange_rate=amount['exchange_rate'])

                tid = str(getattr(transaction_data, 'id'))   
                transaction_id = create_payment_id(transaction_id=tid)
                Transaction_details.objects.filter(id=tid).update(app_version=app_version,platform=platform,transaction_id=transaction_id)
            
            #check transactions account usage limit
            resposne =  payment_usage_check_mobile(request.user.id, request.user.customer_id, transaction_id)
            if resposne:
                code = "400"
                message = "You have reached your transaction limit , please upgrade your tier to continue transaction or try with lesser amount."
                new_response = {
                "code": code,
                "message": message,
                "cross_payment_limit": "True"
                }   
                return Response(new_response)

            return success_response(message="success", data={'transaction_id':transaction_id})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))


class Create_Update_Transaction_Mobile_View(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]  

    def post(self,request,format=None):
        transaction_id = request.data.get("transaction_id")
        amount = request.data.get("amount")
        recipient_id = request.data.get("recipient_id")
        app_version = request.data.get('app_version')
        platform = request.data.get('platform')

        
        try:
            user_serializer = User_Profile_Serializer(request.user)
            customer_id = user_serializer.data['customer_id']
            send_method = None
            send_method = amount['send_method']
            is_digital_Id_verified = user_serializer.data['is_digital_Id_verified']
           
            if not transaction_id and not amount:
                return bad_response(message="Please enter transaction_id or amount details.")  
            if transaction_id:
                
                if not Transaction_details_dump.objects.filter(transaction_id=transaction_id, customer_id=customer_id).exists():
                    return bad_response(message="Invalid transaction_id")             
                if amount:
                    Transaction_details_dump.objects.filter(transaction_id=transaction_id).update(send_method=send_method, send_currency=str(amount['send_currency']).upper(), amount=str(amount['send_amount']), total_amount=str(amount['send_amount']),payout_partner = str(amount['payout_partner']),receive_amount= str(amount['receive_amount']),receive_method= str(amount['receieve_method']) ,receive_currency=str(amount['receive_currency']).upper(), reason=amount['reason'], exchange_rate=amount['exchange_rate'], updated_at=get_current_datetime())       
                if recipient_id:
                    if Recipient.objects.filter(id=recipient_id).exists():
                        name = Recipient.objects.filter(id=recipient_id).values('first_name','last_name')
                        recipient_name= str(name[0]['first_name'])+" "+str(name[0]['last_name'])
                        Transaction_details_dump.objects.filter(transaction_id=transaction_id).update(recipient_name=recipient_name,recipient=recipient_id,risk_score="NA", risk_group="NA",tm_status="NA", tm_label = "NA", updated_at=get_current_datetime())
            else:
                transaction_data = Transaction_details_dump.objects.create(app_version=app_version,platform=platform,payment_status=transaction['incomplete'], send_method=send_method,payout_partner = str(amount['payout_partner']),recipient=recipient_id,risk_score="NA", risk_group="NA", tm_status="NA", tm_label = "NA",  customer_id=customer_id, send_currency=str(amount['send_currency']).upper(), amount=str(amount['send_amount']), total_amount = str(amount['send_amount']),receive_amount= str(amount['receive_amount']), receive_method= str(amount['receieve_method']),receive_currency=str(amount['receive_currency']).upper(), reason=amount['reason'], exchange_rate=amount['exchange_rate'])
                # if is_digital_Id_verified == "approved":
                #     transaction_data = Transaction_details.objects.create(app_version=app_version,platform=platform,payment_status=transaction['incomplete'], send_method=send_method,payout_partner = str(amount['payout_partner']),recipient=recipient_id,risk_score="NA", risk_group="NA", tm_status="NA", tm_label = "NA",  customer_id=customer_id, send_currency=str(amount['send_currency']).upper(), amount=str(amount['send_amount']), total_amount = str(amount['send_amount']),receive_amount= str(amount['receive_amount']), receive_method= str(amount['receieve_method']),receive_currency=str(amount['receive_currency']).upper(), reason=amount['reason'], exchange_rate=amount['exchange_rate'])
                
                tid = str(getattr(transaction_data, 'id'))   
                transaction_id = create_payment_id(transaction_id=tid)
                Transaction_details_dump.objects.filter(id=tid).update(app_version=app_version,platform=platform,transaction_id=transaction_id)
          
            return success_response(message="success", data={'transaction_id':transaction_id})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))



#registering payid and fetching payid from db
class Zai_register_payid_peruser_View(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            transaction_id = request.data.get("transaction_id")
            app_version = request.data.get('app_version')
            platform = request.data.get('platform')

            if not transaction_id:
                return bad_response("Please enter transaction_id") 
            if not Transaction_details.objects.filter(transaction_id=transaction_id).exists():
                return bad_response("Invalid transaction_id")
            
            obj = Transaction_details.objects.filter(transaction_id=transaction_id).values_list('customer_id', flat=True)
            userDetailOcc = User.objects.filter(customer_id__in=obj).values('is_digital_Id_verified')[0]
            is_digital_Id_verified = userDetailOcc['is_digital_Id_verified']
            if is_digital_Id_verified != "approved":
                sa = User.objects.filter(customer_id__in=obj).update(user_check="spam")
                return Response({"code":"401","message":"Your account isn't verified. Log in to WidophRemit.com to complete KYC."},status=status.HTTP_401_UNAUTHORIZED)

            Transaction_details.objects.filter(transaction_id=transaction_id).update(app_version=app_version,platform=platform,send_method="zai_payid_per_user")
            obj = Transaction_details.objects.filter(transaction_id=transaction_id)
            obj = obj[0]
            if not obj.recipient:
                return bad_response(message="Recipient not found for this transaction")
            profile_serializer = User_Profile_Serializer(request.user)
            access_token = zai_token(request)
            zai_user_id = None 


            obj = Transaction_details.objects.filter(transaction_id=transaction_id).values_list('customer_id', flat=True)
            userDetailOcc = User.objects.filter(customer_id__in=obj).values('occupation','app_update','is_digital_Id_verified')[0]
            update_app = userDetailOcc['app_update']
            # is_digital_Id_verified = userDetailOcc['is_digital_Id_verified']
            # print("iiiiiiiiiiii",is_digital_Id_verified)
            # if is_digital_Id_verified != "approved":
            #     return Response({"code":"401","message":"Your account is logged out because your account is not verified, please log-in into WidophRemit.com website to complete the KYC or reach out to the admin."},status=status.HTTP_401_UNAUTHORIZED)

            if not userDetailOcc['occupation'] and update_app is None:
                # User.objects.filter(customer_id__in=obj).update(occupation="old_user")
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            if userDetailOcc['occupation'] == "old_user":
                return Response(status=status.HTTP_401_UNAUTHORIZED)

            if zai_payid_details.objects.filter(user_id = profile_serializer.data['id']).exists():
                payid_obj = zai_payid_details.objects.filter(user_id = profile_serializer.data['id'])
                payid_obj = payid_obj[0]
                zai_user_id = payid_obj.zai_user_id
                payid = payid_obj.payid
            else:
                zai_email = profile_serializer.data['email']
                # ====search email id in users
                search_response = zai_search_email_id(access_token=access_token, email=zai_email)
                if 'users' in search_response:
                    for i in search_response['users']:
                        if str(i['email']) == zai_email:
                            zai_user_id = i['id']
                            zai_email = i['email']
                    
                if zai_user_id == None:
                    # ========= create zai user
                    user_response = zai_create_user(access_token=access_token, customer_id=profile_serializer.data['customer_id'], email=profile_serializer.data['email'],  mobile=profile_serializer.data['mobile'], fn=profile_serializer.data['First_name'], ln=profile_serializer.data['Last_name'])
                    if 'errors' in user_response:
                        errors = user_response['errors']
                        e = ""
                        for k, v in zip(errors.keys(), errors.values()):
                            k = k.replace("principal.","")
                            if k != "principal":
                                e = e+str(k)+" "+str(v[0])+", "
                        if e.endswith(", "):
                            e = e[:-2]
                        return bad_response(message=e)
                    zai_user_id = user_response['users']['id']
                
                #=== get user walet account id
                wallet_response =  zai_get_user_wallet(access_token=access_token, zai_user_id=zai_user_id)
                if 'errors' in wallet_response:
                    return bad_response(message=wallet_response['errors'])  
                wallet_account_id = wallet_response['wallet_accounts']['id']

                # ==== get virtual account id from wallet account id
                v_list_response = zai_virtual_account_list(access_token=access_token, wallet_account_id=wallet_account_id)
                virtual_account_total = v_list_response['meta']['total']
                if virtual_account_total == 0:
                    #creating virtual account with wallet account id
                    virtual_account_response = zai_create_virtual_account(access_token=access_token, wallet_account_id=wallet_account_id)
                    if 'errors' in virtual_account_response:
                        return bad_response(message=virtual_account_response['errors'])
                    else:
                        virtual_account_id = virtual_account_response['id']
                        virtual_account_number = virtual_account_response['account_number']
                        routing_number = virtual_account_response['routing_number']
                else:
                    virtual_account_id = v_list_response['virtual_accounts'][0]['id']
                    virtual_account_number = v_list_response['virtual_accounts'][0]['account_number']
                    routing_number = v_list_response['virtual_accounts'][0]['routing_number']
                               
                #registering pay id with virtual account id
                payid = zai_create_payid(customer_id=profile_serializer.data['customer_id'])
                payid_response =  zai_register_payid_peruser(access_token=access_token, virtual_account_id=virtual_account_id, payid=payid, customer_id=zai_user_id)
                if 'errors' in payid_response:
                    return bad_response(message=payid_response['errors'])
                zai_payid_details.objects.create(user_id = profile_serializer.data['id'], zai_user_id=zai_user_id, zai_email=zai_email,payid=payid, wallet_account_id=wallet_account_id, bsb_code=routing_number, account_number=virtual_account_number)        
                
           
            payment_status = Transaction_details.objects.filter(transaction_id=transaction_id).values('payment_status','id')
            return success_response(message=payment_status[0]['payment_status'], data={"payid":payid, "id":payment_status[0]['id'],"status":payment_status[0]['payment_status'],"transaction_id":transaction_id})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))


#zai ayment api to a with pay id per user
class Zai_payid_per_user_payment_View(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        referral_meta_id = None
        transaction_id = request.data.get("transaction_id")
        referral_meta_id = request.data.get("referral_meta_id")
        app_version = request.data.get('app_version')
        platform = request.data.get('platform')

        if not transaction_id:
            return bad_response(message="Please enter transaction_id")
        if not Transaction_details.objects.filter(transaction_id=transaction_id).exists():
            return bad_response("Invalid transaction_id")
        try:
            if str(referral_meta_id).lower().strip() == "none" or str(referral_meta_id).strip() == '':
                final_amount = 0
            else:
                final_amount = apply_discount(transaction_id, referral_meta_id)

            user = User_Profile_Serializer(request.user)
            access_token = zai_token(request)    

            # ====== updating transaction in database
            tobj = Transaction_details.objects.filter(transaction_id=transaction_id)        
            tobj = tobj[0]  

            #getting payid details
            if zai_payid_details.objects.filter(user_id= user.data['id']).exists():
                payid_obj = zai_payid_details.objects.filter(user_id= user.data['id'])
                payid_obj = payid_obj[0]
                valid = str(payid_obj.bsb_code)+str(payid_obj.account_number)

            #Transaction table data
            trn = Transaction_details.objects.filter(transaction_id=transaction_id).values('id','send_currency','receive_currency','receive_amount','amount','exchange_rate','recipient_name','recipient','date')     
            res = trn[0]
           
            url = trn[0]['id']
            rec = trn[0]['recipient']
            d=str(url)
            if HOST == "LOCAL":
                val=settings.BASE_URL+"/mobile_payment/receipt/"+d
            if HOST == "TEST":
                val=settings.BASE_URL+"/mobile_payment/receipt/"+d
            if HOST == "LIVE":
                val=settings.BASE_URL+"/mobile_payment/receipt/"+d

            #Sender address
            add = User_address.objects.filter(user_id=request.user.id).values('flat','building','street','city','postcode','state','country','country_code')
            customer_add = add[0]
            
            #Get recipent data
            recipient_data =  Recipient.objects.filter(id=rec).values('first_name','last_name','email','mobile','flat','building','street','city','state','country') 
            rec_data = recipient_data[0]

            bank_data = Recipient_bank_details.objects.filter(recipient=rec).values('account_number','swift_code')
            w = bank_data[0]

            #for get custmoer_name
            us = User.objects.filter(id=request.user.id).values('First_name', 'Last_name','customer_id')
            cus_name = us[0]
            cus_id = cus_name['customer_id']

            #sending money to user wallet
            if settings.HOST != "LIVE":
                send_money_response = zai_send_money_to_wallet(payment_id=transaction_id, access_token=access_token, send_amount=str(tobj.amount), payid=payid_obj.payid, zai_user_id=payid_obj.zai_user_id, valid=valid)
                if 'Message' in send_money_response:
                    return bad_response(message = send_money_response['Message'])
                Transaction_details.objects.filter(transaction_id=transaction_id).update(app_version=app_version,platform=platform,payment_status=transaction['pending_payment'])

            payment_status = Transaction_details.objects.filter(transaction_id=transaction_id).values('send_method','payment_status','id','send_currency', 'receive_currency', 'receive_amount')        
            User.objects.filter(id=user.data['id']).update(source_currency=str(payment_status[0]['send_currency']), destination_currency=str(payment_status[0]['receive_currency']))
            status_data = Transaction_details.objects.filter(transaction_id=transaction_id).values('id','payment_status','transaction_id','recipient','receive_currency','receive_amount','customer_id','send_currency','amount')
            #sending notifications to RA 
            if str(payment_status[0]['payment_status']) != str(transaction['pending_review']):
                Transaction_details.objects.filter(transaction_id=transaction_id).update(app_version=app_version,platform=platform,payment_status=transaction['pending_payment'])
                if Transaction_details.objects.filter(customer_id=cus_id).exists():
                    transactions = Transaction_details.objects.filter(customer_id=cus_id).count()
                    
                    count = User.objects.filter(id=request.user.id).update(transactions=transactions)
                send_sms_to_RA(type="transaction",data={'payment_status':transaction['pending_payment'],'transaction_id':transaction_id,'customer_id':user.data['customer_id'],'send_currency':tobj.send_currency, 'amount': tobj.amount, 'exchange_rate':tobj.exchange_rate})
                # email_to_RA(type="transaction", data={'payment_status':transaction['pending_payment'], 'send_method':"Zai PayID Per User",'transaction_id':transaction_id,'email':user.data['email'],'customer_id':user.data['customer_id'],'send_currency':tobj.send_currency, 'amount': tobj.amount, 'exchange_rate':tobj.exchange_rate})
                email_to_RA(type="transaction", id = transaction_id)
                recipient_mobile = Recipient.objects.filter(id=status_data[0]['recipient']).values('mobile')
                user_email = User.objects.filter(customer_id=status_data[0]['customer_id']).values('email','is_verified','mobile','First_name','Last_name')
                #sending sms to recipient
                send_sms_to_recipient(recipient_mobile=recipient_mobile[0]['mobile'],data={"username":str(user_email[0]['First_name'])+" "+str(user_email[0]['Last_name']),'transaction_id':status_data[0]['transaction_id'],'receive_currency':status_data[0]['receive_currency'], 'receive_amount':status_data[0]['receive_amount']})
                transaction_notify(request,data={'send_currency':status_data[0]['send_currency'], 'send_amount':status_data[0]['amount']})
            notification.objects.create(source_id=status_data[0]['id'], source_type="mobile_transaction", source_detail=str(tobj.amount)+" ("+str(tobj.send_currency+")"), message="Hi! Your payment to WidophRemit for "+str(tobj.send_currency)+" "+str(tobj.amount)+" has been received. We will be in touch soon to confirm settlement. Thank you.")
            payment_status = Transaction_details.objects.filter(transaction_id=transaction_id).values('payment_status','id','amount')        
            print(payment_status, "per user status ================")
            if str(final_amount) == "0":
                final_amount = payment_status[0]['amount']
            return success_response(message=payment_status[0]['payment_status'], data={"id":payment_status[0]['id'],"status":payment_status[0]['payment_status'],"transaction_id":str(tobj.transaction_id),"date":str(res['date']),"account_number":str(w['account_number']),"swift_code":str(w['swift_code']),"custmoer_name":str(cus_name['First_name']+ ' ' +cus_name['Last_name']),"recipient_name":str(res['recipient_name']),"send_currency":str(res['send_currency']),"receive_currency":str(res['receive_currency']),"send_amount":str(res['amount']),"receive_amount":str(res['receive_amount']),"final_amount":final_amount,"exchange_rate":str(res['exchange_rate']),"url":str(val),"sender_address":customer_add,"recipient":rec_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in mobile_payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))



# ===== create agreement API
class Zai_create_payto_agreement_View(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        australia_timezones = pytz.timezone('Australia/Victoria')
        # print("sssssssss",australia_timezones)
        current_time = datetime.now(australia_timezones)
        date_only = current_time.date()
        # print("Current time in York:", date_only)

        payid            = None
        account_id       = None
        bsb              = None
        payid            = request.data.get("pay_id")
        payid_type       = request.data.get("payid_type")
        bsb              = request.data.get("bsb")
        account_number   = request.data.get("account_number")
        agreement_amount = request.data.get('agreement_amount')
        # start_date       = request.data.get('start_date')
        start_date       = date_only

        try:
            if not payid and not account_number:
                return bad_response(message="Please enter PayId or account details")
            if payid:
                if not payid_type:
                    return bad_response(message="Please enter payid_type")
            if account_number:
                if not bsb:
                    return bad_response(message="Please enter BSB code")
            if not agreement_amount:
                return bad_response(message="Please enter agreement amount")
            if not start_date:
                return bad_response(message="Please enter start_date")

            if str(payid_type).upper() == "TELI":
                payid = "+61-"+str(payid)
            profile_serializer = User_Profile_Serializer(request.user)
            access_token = zai_token(request)     
            zai_email = profile_serializer.data['email']
            payid = str(payid).lower()
            payid_type = str(payid_type).upper()
            zai_user_id = None

            
            # ==== search email id in users
            search_response = zai_search_email_id(access_token=access_token, email=zai_email)
            if 'users' in search_response:
                for i in search_response['users']:
                    if str(i['email']) == zai_email:
                        zai_user_id = i['id']
                        zai_email = i['email']
                    
            if zai_user_id == None:
                # ========= create zai user
                user_response = zai_create_user(access_token=access_token, customer_id=profile_serializer.data['customer_id'], email=profile_serializer.data['email'],  mobile=profile_serializer.data['mobile'], fn=profile_serializer.data['First_name'], ln= profile_serializer.data['Last_name'])
                if 'errors' in user_response:
                    errors = user_response['errors']
                    e = ""
                    for k, v in zip(errors.keys(), errors.values()):
                        k = k.replace("principal.","")
                        if k != "principal":
                            e = e+str(k)+" "+str(v[0])+", "
                    if e.endswith(", "):
                        e = e[:-2]
                    return bad_response(message=e)
                zai_user_id = user_response['users']['id']

            # ===== validate PayTo agrement
            if payid == "none":
                account_id = str(bsb)+str(account_number)
            validate_agreement_response = zai_validate_payto_agreement(fn = profile_serializer.data['First_name'], ln=profile_serializer.data['Last_name'], payid_type=payid_type, user_email= profile_serializer.data['email'],access_token=access_token, zai_user_id=zai_user_id, payid=payid, start_date=str(start_date), account_id=account_id, agreement_amount=agreement_amount )
            if 'errors' in validate_agreement_response:
                return bad_response(message=validate_agreement_response['errors'])
            agreement_uuid = validate_agreement_response['agreement_uuid']
            agreement_status = validate_agreement_response['status']
            print(agreement_status, "=========")

            # ===== create agreement
            agreement_response = zai_create_agreement( agreement_uuid=agreement_uuid, access_token=access_token)
            if agreement_status == "VALIDATION_FAILED":
                return bad_response(message=agreement_response)
            if 'errors' in agreement_response:
                return bad_response(message=agreement_response['errors'])

            # ========= save agreement details in DB
            validity_end_date = zai_agreement_end_date(start_date)
            if zai_agreement_details.objects.filter(user_id=profile_serializer.data['id']).exists():
                zai_agreement_details.objects.filter(user_id=profile_serializer.data['id']).update(zai_user_id=zai_user_id, zai_email=zai_email, status=str(agreement_status).lower() , payid=payid, payid_type=str(payid_type).upper(), agreement_start_date=start_date, account_number=account_number, wallet_account_id=None, bsb_code=bsb, agreement_uuid=agreement_uuid, max_amount=agreement_amount,agreement_end_date=str(validity_end_date))
            else:
                zai_agreement_details.objects.create(user_id=profile_serializer.data['id'], status=str(agreement_status).lower() ,zai_user_id=zai_user_id, zai_email=zai_email, payid=payid, payid_type=str(payid_type).upper(), agreement_start_date=start_date, account_number=account_number, wallet_account_id=None, bsb_code=bsb, agreement_uuid=agreement_uuid, max_amount=agreement_amount,agreement_end_date=str(validity_end_date))
            print("agreement created ======")
            return success_response(message="Agreement has been created successfully. Please authorise it.", data={"agreement_uuid":agreement_uuid})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in mobile_payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
          
    
#zai payment API with pay to (PayTo Agreement)
class Zai_payto_agreement_payment_View(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        referral_meta_id = None
        referral_meta_id = request.data.get("referral_meta_id")
        agreement_uuid = request.data.get("agreement_uuid")
        transaction_id = request.data.get('transaction_id')
        app_version = request.data.get('app_version')
        platform = request.data.get('platform')

        if not agreement_uuid:
            return bad_response(message="Please enter agreement_uuid")
        if not transaction_id:
            return bad_response(message="Please enter transaction_id")
        try:
            if not Transaction_details.objects.filter(transaction_id=transaction_id).exists():
                return bad_response(message="Invalid transaction_id")
            Transaction_details.objects.filter(transaction_id=transaction_id).update(app_version=app_version,platform=platform,send_method="zai_payto_agreement", updated_at=get_current_datetime(), date=get_current_date())
            obj = Transaction_details.objects.filter(transaction_id=transaction_id)
            obj = obj[0]
            if not obj.recipient:
                return bad_response(message="Recipient not found for this transaction")
            
            profile_serializer = User_Profile_Serializer(request.user)
            user_id = request.user.id
            access_token = zai_token(request)     
            zai_email = profile_serializer.data['email']
            payment_id = None

            if str(referral_meta_id).lower().strip() == "none" or str(referral_meta_id).strip() == '':
                final_amount = 0
            else:
                final_amount = apply_discount(transaction_id, referral_meta_id)
            # === get agreement details
            if not zai_agreement_details.objects.filter(user_id=profile_serializer.data['id'], agreement_uuid=agreement_uuid).exists():
                return bad_response(message="Invalid agreement_uuid")
            agreement_details = zai_get_agreement_details(agreement_uuid=agreement_uuid, access_token=access_token)
            agreement_status = agreement_details['status']
            agreement_uuid = agreement_details['agreement_uuid']
            zai_user_id = agreement_details['user_external_id']

            print(agreement_status, "status of agreement  ======================")
            if settings.HOST == 'LIVE':
                payid_owner_name = agreement_details['agreement_info']['debtor_info']['debtor_account_details']['payid_details']['payid_name']

                #matching payid owner name with user name
                user_name = str(request.user.First_name).lower()+" "+str(request.user.Last_name).lower()
                if str(payid_owner_name).lower() != user_name:
                    status_obj = zai_update_agreement_status(agreement_uuid, access_token, "name linked to PayID does not match the name provided during registration")
                    if status_obj and zai_agreement_details.objects.filter(user_id=user_id, agreement_uuid=agreement_uuid).exists():
                        zai_agreement_details.objects.filter(user_id=user_id, agreement_uuid=agreement_uuid).update(status='cancelled')
                    return Response({"code":"400","message":"Your agreement has been canceled as the name linked to your PayID does not match the name provided during registration.", "data":{"id":obj.id,"transaction_id":obj.transaction_id, 'final_amount':str(obj.amount)}})


            if str(agreement_status).lower() != "active":
                Transaction_details.objects.filter(transaction_id=transaction_id).update(app_version=app_version,platform=platform,payment_status=transaction['pending_payment'])
                return Response({"code":"400","message":transaction['pending_payment'], "data":{"id":obj.id,"transaction_id":obj.transaction_id,'final_amount':str(obj.amount)}})
            else:
                Transaction_details.objects.filter(transaction_id=transaction_id).update(app_version=app_version,platform=platform,payment_status=transaction['pending_payment'])
                zai_agreement_details.objects.filter(user_id=user_id, agreement_uuid=agreement_uuid).update(status='active')
                

            # === getting recipient bank details
            if not Recipient.objects.filter(id=obj.recipient).exists():
                return bad_response(message="Invalid recipient")
            recipient = Recipient.objects.filter(id=obj.recipient)
            recipient = recipient[0]
            
            if Recipient_bank_details.objects.filter(recipient_id=obj.recipient).exists():
                bank = Recipient_bank_details.objects.filter(recipient_id=obj.recipient)
                bank = bank[0]

            if User_address.objects.filter(user_id=profile_serializer.data['id']).exists():
                address = User_address.objects.filter(user_id=profile_serializer.data['id'])
                address = address[0]
            
             #Transaction table data
            trn = Transaction_details.objects.filter(transaction_id=transaction_id).values('id','send_currency','receive_currency','receive_amount','amount','exchange_rate','recipient_name','recipient','date')     
            res = trn[0]
            
            url = trn[0]['id']
            rec = trn[0]['recipient']
            d=str(url)
            if HOST == "LOCAL":
                val=settings.BASE_URL+"/mobile_payment/receipt/"+d
            if HOST == "TEST":
                val=settings.BASE_URL+"/mobile_payment/receipt/"+d
            if HOST == "LIVE":
                val=settings.BASE_URL+"/mobile_payment/receipt/"+d

            #Sender address
            add = User_address.objects.filter(user_id=request.user.id).values('flat','building','street','city','postcode','state','country','country_code')
            customer_add = add[0]
            

            #Get recipent data
            recipient_data =  Recipient.objects.filter(id=rec).values('first_name','last_name','email','mobile','flat','building','street','city','state','country') 
            rec_data = recipient_data[0]

            bank_data = Recipient_bank_details.objects.filter(recipient=rec).values('account_number','swift_code')
            w = bank_data[0]

             #for get custmoer_name
            us = User.objects.filter(id=request.user.id).values('First_name', 'Last_name','customer_id')
            cus_name = us[0]
            cus_id = cus_name['customer_id']
          
            #payment initiate request
            initiate_response = zai_initiate_payment(access_token=zai_token(request), agreement_uuid=agreement_uuid, send_amount=str(obj.amount), payment_id=transaction_id, reason=obj.reason)
            if 'errors' in initiate_response:
                return bad_response(message=initiate_response['errors'])
            
            # ============= Fraudnet transaction check api
            fraudnet_payment_status="approved" 
            fraudnet_response = zai_fraudnet_tranaction_check(fraudnet_payment_status, recipient_account_number = str(bank.account_number), transaction_id= str(obj.id), send_currency=str(obj.send_currency), send_amount=str(obj.amount),  payment_id=str(transaction_id), recipient_id=str(obj.recipient),recipient_country_code = str(recipient.country_code), recipient_address= str(recipient.building+" "+recipient.street+" "+recipient.city+" "+recipient.state), recipient_name = str(recipient.first_name+" "+recipient.last_name), customer_postcode = address.postcode, customer_country_code = address.country_code, customer_dob = str(profile_serializer.data['Date_of_birth']) ,customer_mobile = str(profile_serializer.data['mobile']), customer_email = str(profile_serializer.data['email']), customer_id = str(profile_serializer.data['customer_id']), customer_fn = str(profile_serializer.data['First_name']), customer_ln = str(profile_serializer.data['Last_name']), customer_address=str(address.building+" "+address.street+" "+address.city+" "+address.state), customer_city = address.city,customer_state= address.state)
            print(fraudnet_response, "fraudnet_response ==========")
            if 'data' in fraudnet_response:
                da = update_fn_data_in_db(response=fraudnet_response, customer_id=profile_serializer.data['customer_id'], transaction_id=obj.id)
            payment_status = Transaction_details.objects.filter(transaction_id=transaction_id).values('send_method','payment_status','id','send_currency' ,'receive_currency', 'receive_amount','customer_id','amount')
            User.objects.filter(id=profile_serializer.data['id']).update(source_currency=str(payment_status[0]['send_currency']), destination_currency=str(payment_status[0]['receive_currency']))
            notification.objects.create(source_id=payment_status[0]['id'], source_type="mobile_transaction", source_detail=str(obj.amount)+" ("+str(obj.send_currency)+")", message="Hi! Your payment to WidophRemit for "+str(payment_status[0]['send_currency'])+" "+str(payment_status[0]['amount'])+" has been received. We will be in touch soon to confirm settlement. Thank you.")
            if Transaction_details.objects.filter(customer_id=cus_id).exists():
                transactions = Transaction_details.objects.filter(customer_id=cus_id).count()
                # cou_str = str(transactions)
                # print("pppppp",cou_str)
                count = User.objects.filter(id=request.user.id).update(transactions=transactions)
            send_sms_to_RA(type="transaction",data={'payment_status':payment_status[0]['payment_status'],'transaction_id':transaction_id,'customer_id':profile_serializer.data['customer_id'],'send_currency':obj.send_currency, 'amount': obj.amount, 'exchange_rate':obj.exchange_rate})
            # email_to_RA(type="transaction", data={'payment_status':payment_status[0]['payment_status'],'send_method':"Zai PayTo Agreement",'transaction_id':transaction_id,'email':profile_serializer.data['email'],'customer_id':profile_serializer.data['customer_id'],'send_currency':obj.send_currency, 'amount': obj.amount, 'exchange_rate':obj.exchange_rate})
            email_to_RA(type="transaction", id = transaction_id)
            transaction_notify(request,data={'send_currency':payment_status[0]['send_currency'], 'send_amount':payment_status[0]['amount']})
            #sending transaction email receipt to customer
            email_transaction_receipt_mobile(type="create_transaction",transaction_id=transaction_id)
            pr = send_sms_to_customer(type= "customer",data={'transaction_id':transaction_id,'send_currency':obj.send_currency, 'send_amount':obj.amount}, user_mobile=profile_serializer.data['mobile'])
            print("send_smssss",pr)
            #fetching discounted amount to return in response
            if str(final_amount) == "0":
                final_amount = payment_status[0]['amount']
            return success_response(message=payment_status[0]['payment_status'], data={"id":str(obj.id),"status":payment_status[0]['payment_status'],"transaction_id":str(transaction_id),"date":str(res['date']),"account_number":str(w['account_number']),"swift_code":str(w['swift_code']),"custmoer_name":str(cus_name['First_name']+ ' ' +cus_name['Last_name']),"recipient_name":str(res['recipient_name']),"send_currency":str(res['send_currency']),"receive_currency":str(res['receive_currency']),"send_amount":str(res['amount']),"receive_amount":str(res['receive_amount']),"final_amount":final_amount,"exchange_rate":str(res['exchange_rate']),"url":str(val),"sender_address":customer_add,"recipient":rec_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in mobile_payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

def dateformat(date):
    date = str(date)
    return datetime.strptime(date, '%Y-%m-%d') 

class Zai_list_agreement_View(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            data = None
            send_amount = request.data.get('send_amount')
            profile_serializer = User_Profile_Serializer(request.user)
            is_digital_Id_verified = profile_serializer.data['is_digital_Id_verified']
            customer_id = profile_serializer.data['customer_id']
            
            print("dsdfsd",is_digital_Id_verified)
            if is_digital_Id_verified != "approved":
                User.objects.filter(customer_id=customer_id).update(user_check="spam")
                return Response({"code":"401","message":"Your account isn't verified. Log in to WidophRemit.com to complete KYC."},status=status.HTTP_401_UNAUTHORIZED)
            occ = profile_serializer.data['occupation']
            update_app = User.objects.get(id=request.user.id)
            da = User.objects.filter(email=update_app).values('app_update')[0]
            use = da['app_update']
            if occ is None and use is None:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            if occ == "old_user":
                
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            
            if zai_agreement_details.objects.filter(user_id=profile_serializer.data['id'],status='active').exists():
                data = zai_agreement_details.objects.filter(user_id=profile_serializer.data['id'],status='active').values('payid','agreement_start_date','agreement_end_date','account_number','bsb_code','max_amount','status','agreement_uuid')

            elif zai_agreement_details.objects.filter(user_id=profile_serializer.data['id']).exclude(Q(status='cancelled') | Q(status="canceled")).exists():
                data = zai_agreement_details.objects.filter(user_id=profile_serializer.data['id']).exclude(Q(status='cancelled') | Q(status="canceled")).values('payid','payid_type','agreement_start_date','agreement_end_date','account_number','bsb_code','max_amount','status','agreement_uuid')    
            if data:
                agreement_details = zai_get_agreement_details(agreement_uuid=str(data[0]['agreement_uuid']), access_token=zai_token(request))
                data = dict(data[0])
                account_id_type = agreement_details['agreement_info']['debtor_info']['debtor_account_details']['account_id_type']
                data.update(account_id_type=account_id_type)
                #updating status for expired agreement for QA server
                if HOST != "Live" and data['agreement_end_date'] is not None:
                    if str(data['agreement_end_date']).strip() != "":
                        end_date = datetime.strptime(str(data['agreement_end_date']), "%Y-%m-%d").date()
                        if end_date < get_current_date():
                            zai_agreement_details.objects.filter(agreement_uuid=data['agreement_uuid']).update(status='cancelled')
                            data['status'] = 'cancelled'
                if data['payid'] == "none":
                    del data['payid']
                else:
                    del data['bsb_code']
                    del data['account_number']
                if data['status'] == "expired":
                    # data.delete()
                    return bad_response(message="No agreement created")
                if data['status'] != "active" and data['status'] != 'cancelled' and data['status'] != 'canceled':
                    return success_response("Please authorise agreement.", data)
                
                fa = zai_agreement_details.objects.filter(user_id=profile_serializer.data['id'], status='cancelled').values()
                if fa:
                    agreement_end_date_str = fa[0].get('agreement_end_date')
                    if agreement_end_date_str and datetime.strptime(agreement_end_date_str, '%Y-%m-%d') < datetime.today():
                        return Response({"code": "406", 'expired': True, "message": "Your agreement validity period has been expired. Please create new agreement."})
                else:
                    return success_response(message="success", data=data)
            elif zai_agreement_details.objects.filter(user_id=profile_serializer.data['id'], status='cancelled').exists():
                data = zai_agreement_details.objects.filter(user_id=profile_serializer.data['id'], status='cancelled').values()
                if dateformat(data[0]['agreement_end_date']) < datetime.today():
                    return Response({"code": "406", 'expired': True, "message": "Your agreement validity period has been expired. Please create new agreement."})
                return Response({"code": "400", 'expired': False, "message": "Agreement has not been created."})
            else:
                return Response({"code": "400", 'expired': False, "message": "Agreement has not been created."})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))



class Zai_update_agreement_View(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            validity_end_date = None
            transaction_id   = request.data.get('transaction_id')
            agreement_amount = request.data.get('agreement_amount')
            agreement_uuid   = request.data.get('agreement_uuid')

            if not agreement_amount:
                return bad_response(message="Please enter agreement amount")
            if not agreement_uuid:
                return bad_response(message="Please enter agreement_uuid")

            profile_serializer = User_Profile_Serializer(request.user)
            access_token = zai_token(request)     
            zai_email = profile_serializer.data['email']
            send_currency = "AUD"
            
             #Transaction table data
            trn = Transaction_details.objects.filter(transaction_id=transaction_id).values('id','transaction_id','send_currency','receive_currency','receive_amount','amount','exchange_rate','recipient_name','recipient','date')     
            res = trn[0]
        
            url = trn[0]['id']
            rec = trn[0]['recipient']
            d=str(url)
            # val="http://127.0.0.1:8000/mobile_payment/receipt/"+d
            # val="https://api.remitassure.com/mobile_payment/receipt/"+d
            if HOST == "LOCAL":
                val=settings.BASE_URL+"/mobile_payment/receipt/"+d
            if HOST == "TEST":
                val=settings.BASE_URL+"/mobile_payment/receipt/"+d
            if HOST == "LIVE":
                val=settings.BASE_URL+"/mobile_payment/receipt/"+d

            #Sender address
            add = User_address.objects.filter(user_id=request.user.id).values('flat','building','street','city','postcode','state','country','country_code')
            customer_add = add[0]
            
            #Get recipent data
            recipient_data =  Recipient.objects.filter(id=rec).values('first_name','last_name','email','mobile','flat','building','street','city','state','country') 
            rec_data = recipient_data[0]

            bank_data = Recipient_bank_details.objects.filter(recipient=rec).values('account_number','swift_code')
            w = bank_data[0]

            #for get custmoer_name
            us = User.objects.filter(id=request.user.id).values('First_name', 'Last_name')
            cus_name = us[0]
            #for get create_date
            # v = Transaction_details.objects.filter(transaction_id=transaction_id).values('created_at').first()['created_at']
            # v_datetime = datetime.strptime(str(v), '%Y-%m-%d %H:%M:%S.%f')
            # date_part = v_datetime.date()
            # date_val = date_part.strftime('%Y-%m-%d')
            
            if not zai_agreement_details.objects.filter(zai_email=zai_email, agreement_uuid=agreement_uuid).exists():
                return bad_response(message="Invalid agreement_uuid")

            update_response = zai_update_agreement(agreement_uuid=agreement_uuid, access_token=access_token, agreement_amount=agreement_amount)
            zai_agreement_details.objects.filter(zai_email=zai_email, agreement_uuid=agreement_uuid).update(agreement_end_date=validity_end_date,agreement_uuid=agreement_uuid, max_amount=agreement_amount, status="pending_amendment_authorisation")

            if 'errors' in update_response:
                return bad_response(message=update_response['errors'][0]['error_message'])     
            return success_response(message="Agreement has been updated. Please authorise it.", data={"agreement_uuid":agreement_uuid,"date":str(res['date']),"account_number":str(w['account_number']),"swift_code":str(w['swift_code']),"custmoer_name":str(cus_name['First_name']+ ' ' +cus_name['Last_name']),"recipient_name":str(res['recipient_name']),"transaction_id":str(res['transaction_id']),"send_currency":str(res['send_currency']),"receive_currency":str(res['receive_currency']),"send_amount":str(res['amount']),"receive_amount":str(res['receive_amount']),"exchange_rate":str(res['exchange_rate']),"url":str(val),"sender_address":customer_add,"recipient":rec_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))


class Pending_Transactions_View(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]  

    def get(self,request,format=None):
        try:
            user_serializer = UserProfileSerializer(request.user)
            customer_id = user_serializer.data['customer_id']
            if not Transaction_details.objects.filter(customer_id=customer_id, payment_status=transaction['incomplete']).exists():
                return bad_response(message="No transactions found.")             
            data = Transaction_details.objects.filter(customer_id=customer_id, payment_status=transaction['incomplete'])
            serializer = Transaction_details_web_Serializer(data, many=True)
            return success_response(message="success", data=serializer.data)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))


class transaction_summary(APIView):
    # renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]  

    def post(self, request, format=None):
        type = request.data.get('type')
        user = User_Profile_Serializer(request.user)
        transaction_id = request.data.get('transaction_id')
        if not transaction_id:
            return bad_response(message="Please enter transaction id")
        if not Transaction_details.objects.filter(transaction_id=transaction_id).exists():
            return bad_response(message="Incorrect transaction id")
        if not Transaction_details.objects.filter(customer_id=user.data['customer_id'], transaction_id=transaction_id).exists():
            return bad_response(message="Transaction not found for this recipient")
        tdata = Transaction_details.objects.filter(customer_id= user.data['customer_id'], transaction_id=transaction_id).values('id', 'recipient','exchange_rate', 'date', 'tm_label','transaction_id','card_type','recipient_name','customer_id','recipient','send_currency','receive_currency','amount','send_method', 'receive_amount','receive_method', 'payment_status', 'payment_status_reason','tm_status','reason','created_at', 'risk_score','risk_group')
        if not Recipient_bank_details.objects.filter(recipient_id=tdata[0]['recipient']).exists():
            return bad_response(message="Bank details not found")      
        bank_data = Recipient_bank_details.objects.filter(recipient_id=tdata[0]['recipient']).values('bank_name','account_name','account_number')
        customer_name = str(user.data['First_name'])+" "+str(user.data['Last_name'])
        send_method_details = None
        if tdata[0]['send_method'] == "zai_payto_agreement":
            if zai_agreement_details.objects.filter(user_id=user.data['id']).exists():
                send_method_details = zai_agreement_details.objects.filter(user_id=user.data['id']).values('payid','payid_type','bsb_code','account_number','max_amount')
                send_method_details =send_method_details[0]  
                if send_method_details['payid_type'] == "TELI":
                    if "+61-" in send_method_details['payid']:
                        payid_value = str(send_method_details['payid']).replace("+61-","")     
                        send_method_details["payid"] = payid_value
                   
        elif tdata[0]['send_method'] == "zai_payid_per_user":
            if zai_payid_details.objects.filter(user_id=user.data['id']).exists():
                send_method_details = zai_payid_details.objects.filter(user_id=user.data['id']).values('payid','bsb_code','account_number')
                send_method_details =send_method_details[0]
        # merging two dictionaries of recipient data and bank data        
        dict = tdata[0].copy()
        dict.update(bank_data[0])
        dict.update(customer_name=customer_name, send_amount=tdata[0]['amount'])
        for key in dict:
            if dict[key] is None:
                dict[key] = "" 
            dict[key] = str(dict[key]) 
        dict.update(send_method_details=send_method_details)
        return success_response(message="success", data=dict)


""" Single Transaction Summary """
class transaction_summary_v1(APIView):
    permission_classes=[IsAuthenticated]  

    def post(self, request, format=None):
        bank_data = None
        type = request.data.get('type')
        transaction_id = request.data.get('transaction_id')

        if not transaction_id:
            return bad_response("Please enter transaction id")
        if not is_obj_exists(Transaction_details, {'transaction_id':transaction_id}):
            return bad_response("Transaction does not exists!")
        if not is_obj_exists(Transaction_details, {'transaction_id':transaction_id, 'customer_id':request.user.customer_id}):
            return bad_response("Transaction not found for this customer")
        
        tdata = Transaction_details.objects.filter(customer_id= request.user.customer_id, transaction_id=transaction_id).values('id', 'recipient','exchange_rate', 'date', 'tm_label','transaction_id','card_type','recipient_name','customer_id','recipient','send_currency','receive_currency','amount','send_method', 'receive_amount','receive_method', 'payment_status', 'payment_status_reason','tm_status','reason','updated_at', 'risk_score','risk_group','discount_amount','total_amount')
        if tdata[0]['recipient'] and str(tdata[0]['recipient']).strip() != '' and is_obj_exists(Recipient_bank_details, {'recipient_id':tdata[0]['recipient']}):
            bank_data = Recipient_bank_details.objects.filter(recipient_id=tdata[0]['recipient']).values('bank_name','account_name','account_number')
        customer_name = str(request.user.First_name)+" "+str(request.user.Last_name)
        send_method_details = None
        if tdata[0]['send_method'] == zai['payto']:
            if is_obj_exists(zai_agreement_details, {'user_id':request.user.id}):
                send_method_details = zai_agreement_details.objects.filter(user_id=request.user.id).values('payid','payid_type','bsb_code','account_number','max_amount')
                send_method_details = send_method_details[0]  
                if send_method_details['payid_type'] == "TELI":
                    if "+61-" in send_method_details['payid']:
                        payid_value = str(send_method_details['payid']).replace("+61-","")     
                        send_method_details["payid"] = payid_value
                   
        elif tdata[0]['send_method'] == zai['payid']:
            if is_obj_exists(zai_payid_details, {'user_id':request.user.id}):
                send_method_details = zai_payid_details.objects.filter(user_id=request.user.id).values('payid','bsb_code','account_number')
                send_method_details = send_method_details[0]

        # merging two dictionaries of recipient data and bank data        
        dict = tdata[0].copy()
        if bank_data:
            dict.update(bank_data[0])
        else:
            dict.update(bank_name=None, account_name=None, account_number=None)
        dict.update(customer_name=customer_name, send_amount=tdata[0]['amount'])
        if not dict['total_amount'] or str(dict['total_amount']) == "0.0000" or str(dict['total_amount']) == "0":
            dict['total_amount'] = comma_value(dict['amount'])
        else:
            dict['total_amount'] = comma_value(dict['total_amount'])
        dict['amount'] = comma_value(dict['amount'])
        dict['exchange_rate'] = comma_value(dict['exchange_rate'])
        dict['discount_amount'] = comma_value(dict['discount_amount'])
        dict['receive_amount'] = comma_value(dict['receive_amount'])
        for key in dict:
            if dict[key] is None:
                dict[key] = "" 
            dict[key] = str(dict[key]) 
        if send_method_details:
            dict.update(send_method_details=send_method_details)
        else:
            dict.update(send_method_details={})

        recipient = dict.get("recipient", "")

        if HOST == "LOCAL":
            val = settings.BASE_URL + f"/mobile_payment/receipt/{recipient}"
        elif HOST == "TEST":
            val = settings.BASE_URL + f"/mobile_payment/receipt/{recipient}"
        elif HOST == "LIVE":
            val = settings.BASE_URL + f"/mobile_payment/receipt/{recipient}"

        dict.update(receipt_url=val)

        return success_response("success", dict)




class Veriff_view(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]

    def post(self, request, format=None):

        user_data=User.objects.get(id=request.user.id)
        url = settings.VERIFF_SESSION_URL
        api_key = settings.VERIFF_API_KEY
        headers = {
            'X-AUTH-CLIENT': api_key,
            'Content-Type': 'application/json'
        }

        data = json.dumps({
        'verification': {
            'callback': 'https://veriff.com',
            'person': {
            'firstName': str(user_data.First_name),
            'lastName': str(user_data.Last_name),
            'idNumber': str(user_data.mobile),
            },
           'vendorData': str(user_data.customer_id)
        }
    })
        response = requests.post(url, data=data, headers=headers)
        # print(response.json())
        return Response({'code':"200", 'message':"success",'data':response.json()})


class VeriffStatus_View(APIView):
    permission_classes=[IsAuthenticated]

    def post(self, request, format=None):
        status = request.data.get("status")
        if status == "done":
            da = User.objects.filter(id=request.user.id).update(aml_pep_status=False)
            return Response({'code':"200", 'message':"success"})
        else :
            return Response({'code':"401", 'message':"Unauthorized"})

#Veriff API to get session details about user verification status          
class veriff_session_decision_View(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]

    def post(self,request,format=None):
        try:
            status = None
            session_id = request.data.get('session_id')
            if not session_id:
                return bad_response(message="Please enter session_id")
            profile_serializer = UserProfileSerializer(request.user)
            secret_key = settings.VERIFF_SECRET_KEY           
            signature = hmac.new(secret_key.encode('utf-8'),session_id.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
            url = settings.VERIFF_URL+"/v1/sessions/"+session_id+"/decision"
            headers = {'Content-Type': 'application/json', 'X-AUTH-CLIENT': settings.VERIFF_API_KEY, 'X-HMAC-SIGNATURE': signature }
            response = requests.request("GET", url, headers=headers)
            response = response.json()
            customer_id = profile_serializer.data['customer_id']

            if response['verification'] == None:
                if not Veriff.objects.filter(customer_id=customer_id).exists():
                    Veriff.objects.create(customer_id=customer_id)
            else:
                status = response['verification']['status']
                id_type = response['verification']['document']['type']
                id_country = response['verification']['document']['country']
                id_number = response['verification']['document']['number']
                gender = response['verification']['person']['gender']               
                first_name = response['verification']['person']['firstName']
                last_name = response['verification']['person']['lastName']
                ip = response['technicalData']['ip']
                customer_id = response['verification']['vendorData']
                dob = response['verification']['person']['dateOfBirth']
                if not Veriff.objects.filter(customer_id=customer_id).exists():
                    Veriff.objects.create(customer_id=customer_id, first_name=first_name,last_name=last_name, id_type=id_type, id_number=id_number,id_country=id_country, ip=ip, status=status)
                else:
                    Veriff.objects.filter(customer_id=customer_id).update(first_name=first_name,last_name=last_name, id_type=id_type, id_number=id_number,id_country=id_country, ip=ip, status=status)
            if str(status).lower() == "approved":
                User.objects.filter(customer_id=customer_id, is_superuser=False).update(aml_pep_status=True, is_digital_Id_verified=status)
                
                last = Transaction_details_dump.objects.filter(customer_id=customer_id).values().last()
                last.pop('id', None)
                new_transaction = Transaction_details(**last)
                new_transaction.save()

            return success_response(message=status, data=response )
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
 
class notification_list(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request, format=None):
        us = User.objects.filter(id=request.user.id).values('customer_id')[0]
        print("rrr",us)
        data = us['customer_id']
        if Transaction_details.objects.filter(customer_id=data).exists():
            transactions = Transaction_details.objects.filter(customer_id=data).values('id')
            notification_data = notification.objects.filter(source_id__in=transactions, read=False, source_type='mobile_transaction').values('source_id', 'source_type', 'source_detail', 'message', 'created_at').order_by('-created_at')
            all_count = notification.objects.filter(source_id__in=transactions, read=False, source_type='mobile_transaction').count()
            print(notification_data, "notification data")
            notification_data = list(notification_data) 
        if len(notification_data) == 0:
            notifications = {"notification_data": "No data found"}
            return Response(notifications)
        else:
            d = notification_data[0]['created_at']
            date = d.strftime('%Y-%m-%d %H:%M:%S')
            for x in notification_data:
                x['created_at'] = date
                x['title'] = "Transaction complete"
                for key in x:
                    x[key] = str(x[key])
            # all_count = notification.objects.filter(Q(read=False) & Q(source_id=data) & Q(source_type='mobile_transaction')).count()
            read_notifications = notification.objects.filter(read=True).count()
            # read_notifications.update(read=F('read') - 1)
            if read_notifications > 0:
                read_notifications -= 1
            notifications = {
                "notification_data": notification_data,
                "all_count": all_count
            }
        return Response({'code':"200", 'data':notifications})
    


def apply_vouchers(request, user_id, vouchers, transaction_id):
    try:
        discount_amount = 0
        format = '%Y-%m-%d'
        if len(vouchers) > 0:
            for i in vouchers:
                if referral.objects.filter(referral_id=i).exists():                    
                    referral_meta.objects.create(transaction_id=transaction_id, referral_id=i,user_id=user_id, is_used=True)
                    type = referral.objects.filter(referral_id=i).values('referral_type_id','referred_by_amount','referred_to_amount')
                    discount = type[0]['referred_by_amount']
                    if discount is not None:
                        discount_amount += discount
        return {'discount_amount': discount_amount}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))


class voucher_view(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            transaction_id = request.data.get('transaction_id')
            amount =  None
            if transaction_id:
                tobj = Transaction_details.objects.filter(transaction_id=transaction_id).values('amount')
                amount = tobj[0]['amount']
            profile_serializer = UserProfileSerializer(request.user)
            data = referral.objects.all().values('id','referral_type_id','referred_by_amount','referred_to_amount','referral_type_id__type','name','description','status','start_date','end_date')
            array = []
            for i in data:
                if not referral_meta.objects.filter(user_id=profile_serializer.data['id'], referral_id  = i['id']).exists():
                    if str(i['status']).lower() == "active":
                        start_date = datetime.strptime(i['start_date'], '%Y-%m-%d') 
                        end_date = datetime.strptime(i['end_date'], '%Y-%m-%d') 
                        if datetime.now().date() > start_date.date() or datetime.now().date() == start_date.date():
                            if datetime.now().date() < end_date.date() or datetime.now().date() == end_date.date():
                                if int(amount) > int(settings.REFERRAL_AMOUNT):
                                    array.append(i)
            return success_response(message="success",data=array)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        
    def post(self, request, format=None):
        try:
            format = '%Y-%m-%d'
            profile_serializer = UserProfileSerializer(request.user)
            vouchers  = request.data.get('vouchers')
            if not vouchers:
                return bad_response(message="Please enter vouchers")
            for i in vouchers:
                if referral.objects.filter(referral_id=i).exists():
                    referral_meta.objects.create(referral_id=i,user_id=profile_serializer.data['id'], is_used=True)
            return success_response(message="success",data=None)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))



""" Apply Voucher """
class apply_referral_code_view(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            user_id = request.user.id
            referral_meta_id = request.data.get('referral_meta_id')
            transaction_id = request.data.get('transaction_id')
            if str(referral_meta_id).strip() == '' or str(referral_meta_id).lower() == "none":
                return bad_response("Please enter referral_meta_id")
            if str(transaction_id).strip() == '' or str(transaction_id).lower() == "none":
                return bad_response("Please enter transaction_id")
            if not Transaction_details.objects.filter(transaction_id=transaction_id).exists():
                return bad_response("Invalid transaction_id")  
            if not referral_meta.objects.filter(id=referral_meta_id).exists():
                return bad_response("Invalid referral_meta_id")    
            #updating referral meta object           
            referral_meta.objects.filter(id=referral_meta_id, is_used=False).update(transaction_id=transaction_id, claimed=True, claimed_date=get_current_date(), is_used=False)
            obj = referral_meta.objects.filter(id=referral_meta_id, is_used=False).values('discount')
            final_data = discount_calculation(transaction_id=transaction_id, discount_amount=obj[0]['discount'], update=False)                 
            return success_response("success", data=final_data)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        

""" Get Default Referral Discount Amount to show on referrals page on frontend page """
class get_default_referrals_discount_amount(APIView):
    renderer_classes=[UserRenderer]

    def get(self,request,format=None):
        try:
            if referral_type.objects.filter(type=str(referral_dict['invite'])).exists():
                type_id = referral_type.objects.filter(type=str(referral_dict['invite'])).values('id')
                if referral.objects.filter(referral_type_id=type_id[0]['id'], currency="AUD").exists():
                    data = referral.objects.filter(referral_type_id=type_id[0]['id'], currency="AUD").values('referred_by_amount','referred_to_amount')
                    return success_response("success", {'referred_by_amount':data[0]['referred_by_amount'], 'referred_to_amount':data[0]['referred_to_amount']})          
            return success_response("success", {'referred_by_amount':settings.REFERRED_BY_AMOUNT, 'referred_to_amount':settings.REFERRED_TO_AMOUNT})          
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))


""" No of Completed Transaction and Amount Usage Left """
class Transactions_usage_deatils_View(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]  

    def post(self, request, format=None):
        transactions_left = 0
        amount_left = 0
        unlimited = "False"
        try:

            user = User_Profile_Serializer(request.user)    
            user_serializer = user.data
            if not request.user.id:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            
            is_digital_Id_verified = user_serializer['is_digital_Id_verified']
            if is_digital_Id_verified == "submitted":
                return Response({"code":"200","message":"Your KYC has been submitted, please wait for approval ."})
            if is_digital_Id_verified != "approved":
                return Response({"code":"400","message":"Verify Your Account."})
            
            count = Transaction_details.objects.filter(Q(payment_status=transaction['completed']) | Q(payment_status=transaction['pending_review']), customer_id=request.user.customer_id).count()
            amount = Transaction_details.objects.filter(Q(payment_status=transaction['completed']) | Q(payment_status=transaction['pending_review']), customer_id=request.user.customer_id).aggregate(total=Sum('total_amount'))
            total_amount = amount['total']
            payment_per_annum = request.user.payment_per_annum
            value_per_annum = request.user.value_per_annum

            count_value = next((item[key] for item in PAYMENT_PER_ANNUM_LIST for key in item if str(payment_per_annum).lower().strip() == key.lower().strip()), None)
            amount_value = next((item[key] for item in VALUE_PER_ANNUM_LIST for key in item if str(value_per_annum).lower().strip() == key.lower().strip()), None)
            print(count_value, amount_value, "count_value ------- amount_value")
            print(count, amount, "count ==== amount ")
            if count and count != 0:              
                if count_value == 'unlimited':
                    unlimited = "True"
                    transactions_left = None
                else:
                    transactions_left = abs(int(count) - int(count_value))
            else:
                if count_value != 'unlimited':
                    transactions_left = count_value

            if total_amount:
                if amount_value and amount_value == 'unlimited':
                    unlimited = "True"
                    amount_left = None
                else:
                    amount_left = abs(float(total_amount) - float(amount_value))
            else:
                if amount_value == 'unlimited':
                    unlimited = "True"
                    amount_left = None
                    print(amount_left, "amount left if unlimited")
                else:
                    print(amount_left, "amount left if total is none")
                    amount_left = amount_value
            return success_response("success", {'transactions_left':transactions_left, 'amount_left':amount_left, 'unlimited':unlimited})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        

################################ Referral Views ################################  
""" Get list of customer referrals """
class customer_referral_codes_list_view(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, currency):
        try:
            array = []
            filter_currency = str(currency).upper()
            all_vouchers = referral.objects.filter(currency=filter_currency, status="active").values('id','name','description','start_date','end_date','referral_type_id','referral_type_id__type','referred_by_amount','referred_to_amount')
            for a in list(all_vouchers):
                dict = {'name':a['name'], 'description':a['description'], 'discount':a['referred_by_amount']}

                #fetching invite referral coupons
                if str(a['referral_type_id__type']).lower() == str(referral_dict['invite']).lower():
                    invite_data = get_invite_coupons(request, a['id'], request.user.id)
                    if str(invite_data[0]['discount']) != "0":         
                        array = array+invite_data
                
                #fetching birthday coupons
                if str(a['referral_type_id__type']).lower() == str(referral_dict['birthday']).lower():
                    if str(request.user.Date_of_birth).strip() != '' and str(request.user.Date_of_birth).lower() != 'none':                         
                        if str_to_date(request.user.Date_of_birth).month == get_current_date().month:
                            if is_birthday_coupon_used(request.user.id, a['referral_type_id']) == False:
                                dict.update(referral_meta_id = get_birthday_coupon(request.user.id, a['id'], a['referred_by_amount']))
                                array.append(dict)
            return success_response("success", array)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))