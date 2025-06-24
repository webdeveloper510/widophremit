from Remit_Assure.package import *
import json
from django.conf import settings
import requests
from twilio.rest import Client 
from urllib.parse import urlencode



def transaction_notify(request,data):
    serverToken = settings.FIREBASE_SERVERTOKEN
    rec = Recipient.objects.filter(user=request.user.id).values('user_id')[0]
    user_ids = rec['user_id']
    fcm=User.objects.filter(id=user_ids).values_list("fcm_token",flat=True)[0]
    print("ff",fcm)
    if fcm:
        if '.' in str(data['send_amount']):
            amount = float(data['send_amount'])
        else:
            amount = int(data['send_amount'])
        if float(amount) < float(1):
            amount = "{:.4f}".format(amount) 
        else:
            amount = f"{amount:,}"

        # message = "Good news from WidophRemit! "+str(data["username"])+" sent you "+str(data['receive_currency'])+" "+str(receive_amount)+" and your bank account should be credited within 2-3 working days."
        message= "Hi! Your payment to WidophRemit for "+str(data['send_currency'])+" "+str(amount)+" has been received. We will be in touch soon to confirm settlement. Thank you."

        headers = {
                'Content-Type': 'application/json',
                'Authorization': 'key=' + serverToken,
                }

        body = {
                'notification': {'title': 'Transaction Completed','body':message,},
                'to':fcm,
                'priority': 'high',
                #   'data': dataPayLoad,
                }
        response = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(body))
        print(response.status_code)
        print(response.json())
        return HttpResponse(response.json())
    return fcm


def zai_notification(request):
    serverToken = settings.FIREBASE_SERVERTOKEN
    rec = Recipient.objects.filter(user=request.user.id).values('user_id')[0]
    user_ids = rec['user_id']
    fcm=User.objects.filter(id=user_ids).values_list("fcm_token",flat=True)[0]
    print("ff",fcm)
    if fcm:
        message= "Your agreement validity period has been expired. Please create new agreement."

        headers = {
                'Content-Type': 'application/json',
                'Authorization': 'key=' + serverToken,
            }

        body = {
                'notification': {   'title': 'Zai Agreement Update.',
                                    'body':message,
                                    },
                'to':fcm,
                'priority': 'high',
                #   'data': dataPayLoad,
                }
        response = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(body))
        print(response.status_code)
        print(response.json())
        return HttpResponse(response.json())
    return fcm