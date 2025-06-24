from Remit_Assure.package import *
from auth_app.model_queries import *
from Remit_Assure.helpers import *
import socket
from datetime import datetime

transaction = settings.TRANSACTION

def dateformat(date):
    date = str(date)
    return datetime.strptime(date, '%Y-%m-%d').date()

def get_ip():
    # Get the hostname
    hostname = socket.gethostname()
    # Get the IP address
    ip_address = socket.gethostbyname(hostname)
    return ip_address

################################ Referrals  ################################  
""" get discounts list related to signup only """
def get_invite_coupons(request, referral_id, user_id):
    try:      
        array = []
        referral_id_data = referral.objects.filter(id=referral_id).values()[0]
        return_dict = {}

        #if user has invited users
        data = filter_model_objs(referral_meta, {'user_id':user_id, 'referred_to__isnull':False, 'is_used':False}, {'id','referred_to'})
        if data:
            referred_to_array = []
            for i in data:
                #updating referral id
                referral_meta.objects.filter(id=i['id']).update(referral_id=referral_id)
                #get referred to user data
                user = filter_model_objs(User, {'id':i['referred_to']}, {'customer_id'})
                #updating data in dict after checking that user has created any transaction or not
                if Transaction_details.objects.filter(Q(payment_status=transaction['pending_review']) | Q(payment_status=transaction['completed']), customer_id=user[0]['customer_id']).exists():
                    update_model_obj(referral_meta, {'id':i['id']}, {'discount':referral_id_data['referred_by_amount']})
                    dict1 = {'referral_meta_id':i['id'], 'discount':referral_id_data['referred_by_amount'], 'name':referral_id_data['name'], 'description':referral_id_data['description']}
                    referred_to_array.append(dict1)
            array = referred_to_array
        #if user was referred by another user
        if is_obj_exists(referral_meta, {'user_id':user_id, 'referred_by__isnull':False, 'is_used':False}):
            data = filter_model_objs(referral_meta, {'user_id':user_id, 'referred_by__isnull':False, 'is_used':False}, {'id','referred_by'})
            referred_by_array = []
            for i in data:
                #updating referral id
                referral_meta.objects.filter(id=i['id']).update(referral_id=referral_id)
                update_model_obj(referral_meta, {'id':i['id']}, {'discount':referral_id_data['referred_to_amount']})
                return_dict.update(referral_meta_id=i['id'], discount=referral_id_data['referred_to_amount'], name=referral_id_data['name'], description=referral_id_data['description'])
                referred_by_array.append(return_dict)
            array = array+referred_by_array
        if len(array) == 0: 
            return [{'discount': 0}]     
        return array
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return None   

""" checking birthday is used or not this year """
def is_birthday_coupon_used(user_id, birthday_type_id):
    try:       
        bdy_referral_id = referral.objects.filter(referral_type_id=birthday_type_id).values('id')
        bdy_referral_ids = [item['id'] for item in bdy_referral_id]        
        #if user has claimed voucher this year
        if referral_meta.objects.filter(user_id=user_id, is_used=True, referral_id__in=bdy_referral_ids, claimed_date__year=get_current_year()).exists():
            return True
        else:
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return str(e)+" in line "+str(exc_tb.tb_lineno)

""" Get birthday coupon """
def get_birthday_coupon(user_id, referral_id, discount):
    try:            
        #if object exists then update
        if referral_meta.objects.filter(user_id=user_id, is_used=False, referral_id=referral_id).exists():
            referral_meta.objects.filter(user_id=user_id, is_used=False, referral_id=referral_id).update(claimed_date=get_current_date(), discount=discount)
            obj = referral_meta.objects.filter(user_id=user_id, is_used=False, referral_id=referral_id).values('id')
            return obj[0]['id']
        else:
            obj = referral_meta.objects.create(user_id=user_id, is_used=False, referral_id=referral_id, claimed_date=get_current_date(), discount=discount)
            return obj.id
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return str(e)+" in line "+str(exc_tb.tb_lineno)

""" Checking is coupon active or expired """
def is_coupon_expired(status, start_date, end_date):
    try:
        if str(status).lower().strip() == "active":
            if str(start_date).strip() != '' or str(start_date).lower() != "none":
                start_date = datetime.strptime(start_date, '%Y-%m-%d') 
            if str(end_date).strip() != '' or str(end_date).lower() != "none":
                end_date = datetime.strptime(end_date, '%Y-%m-%d') 
                if datetime.now().date() > start_date.date() or datetime.now().date() == start_date.date():
                    if datetime.now().date() < end_date.date() or datetime.now().date() == end_date.date():
                        return True
            return False
        else:
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return str(e)+" in line "+str(exc_tb.tb_lineno)  
    
################################ Zai  ################################  
""" Search user email in zai to get zai user id """
def zai_search_email_id(access_token, email):
    try:
        url = settings.ZAI_URL+"/users?search="+email
        headers = {'Accept': 'application/json', 'Authorization': 'Bearer '+access_token}
        search_response = requests.request("GET", url, headers=headers)
        search_response = search_response.json()
        return search_response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return str(e)+" in line "+str(exc_tb.tb_lineno)  
    
""" Create user in zai """
def zai_create_user(access_token, customer_id, email, mobile, fn, ln):
    try:
        url = settings.ZAI_URL+"/users"
        payload = json.dumps({
            "id":customer_id,
            "first_name": fn,
            "last_name": ln,
            "email": email,
            "mobile":mobile,
            "country": "AU"
        })
        headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer '+access_token
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return str(e)+" in line "+str(exc_tb.tb_lineno)  

""" Upate Zai User """   
def zai_update_user(access_token, zai_user_id, first_name, last_name, iso_code, user_address, state, city):
    try:
        url = settings.ZAI_URL+"/users/"+zai_user_id
        payload = json.dumps({
            "first_name": first_name,
            "last_name": last_name,
            "country": iso_code,
            "address_line1":user_address,
            "state":state,
            "city":city
        })
        headers = {'Authorization': 'Bearer '+access_token,'Content-Type': 'application/json' }
        response = requests.request("PATCH", url, headers=headers, data=payload)
        response = response.json()
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return str(e)+" in line "+str(exc_tb.tb_lineno)  
    
""" returning zai error """
def zai_error(response):
    try:
        errors = response['errors']
        e = ""
        for k, v in errors.items():
            k = str(k).replace("principal.","")
            if k != "principal":
                e = e+str(k)+" "+str(v[0])+", "
        if e.endswith(", "):
            e = e[:-2]
        return str(e)+" in zai"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return str(e)+" in line "+str(exc_tb.tb_lineno)  
    
""" Get user wallet id """
def zai_get_user_wallet(access_token, zai_user_id):
    try:
        url = settings.ZAI_URL+"/users/"+str(zai_user_id)+"/wallet_accounts"
        headers = { 'Accept': 'application/json', 'Authorization': 'Bearer '+access_token  }
        response = requests.request("GET", url, headers=headers)
        response = response.json()
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return str(e)+" in line "+str(exc_tb.tb_lineno)  
    
""" Get virtual account """
def zai_virtual_account_list(access_token, wallet_account_id):
    try:
        url = settings.ZAI_URL_ACCOUNT+"/wallet_accounts/"+str(wallet_account_id)+"/virtual_accounts/"
        headers = {'Authorization': 'Bearer '+access_token  }
        response = requests.request("GET", url, headers=headers)
        response = response.json()
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return str(e)+" in line "+str(exc_tb.tb_lineno)  
    
""" Create Bank Account """
def create_zai_bank_account(access_token, user_id, bank_name, account_name, account_number, routing_number, account_type, holder_type):
    try:
        url = ZAI_URL+"/bank_accounts"
        payload = json.dumps({
            "user_id": user_id,
            "bank_name": bank_name,
            "account_name": account_name,
            "routing_number": routing_number,
            "account_number": account_number,
            "account_type": account_type,
            "holder_type": holder_type,
            "country": "AUS"
        })
        headers = {
            'Authorization': 'Bearer '+access_token,
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        print(file_content)
        return str(e)+" in line "+str(exc_tb.tb_lineno)  

""" Create virtual account """
def zai_create_virtual_account(access_token, wallet_account_id):
    try:
        url = settings.ZAI_URL_ACCOUNT+"/wallet_accounts/"+wallet_account_id+"/virtual_accounts"
        headers = {'Authorization': 'Bearer '+access_token }
        response = requests.request("POST", url, headers=headers)
        response = response.json()
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return str(e)+" in line "+str(exc_tb.tb_lineno)  
    
""" Creating payid in zai """
def zai_create_payid(customer_id):
    try:
        customer_id = str(customer_id).lower()
        return customer_id+str(settings.ZAI_PAYID_DOMAIN)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return str(e)+" in line "+str(exc_tb.tb_lineno)  
    
""" Register Payid in zai api """
def zai_register_payid_peruser(access_token, virtual_account_id, payid, customer_id):
    try:
        url = settings.ZAI_URL_ACCOUNT+"/virtual_accounts/"+virtual_account_id+"/pay_ids"
        payload = json.dumps({
        "pay_id": payid,
        "type": "EMAIL",
        "details": {
            "pay_id_name": customer_id,
            "owner_legal_name": customer_id
        }
        })
        headers = { 'Content-Type': 'application/json', 'Authorization': 'Bearer '+access_token  }
        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return None
    
""" Send money to user wallet """
def zai_send_money_to_wallet(payment_id, access_token, send_amount, payid, zai_user_id, valid):
    try:
        send_amount = float_int(send_amount) * 100
        url = settings.ZAI_NPP_URL
        payload = json.dumps({
        "amount": send_amount,
        "payId": payid,
        "remittanceInformation": str(payment_id),
        "vaId": valid
        })
        headers = {'Content-Type': 'application/json','Authorization': 'Bearer '+access_token }
        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return None

""" Generate zai agreement validity end date """
def zai_agreement_end_date(start_date):  
    try: 
        start_date = str(start_date) 
        date = datetime.strptime(start_date, "%Y-%m-%d").date()
        new_date = date+timedelta(days=365)
        return new_date
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
    
""" Validate Zai PayTo Agreement """
def zai_validate_payto_agreement(payid_type, fn, ln, user_email, access_token, zai_user_id, payid, start_date, account_id, agreement_amount ):
    try:
        description = "PayTo Agreement"
        name = str(fn)+" "+str(ln)
        if '.' in str(agreement_amount):
            agreement_amount = int(round(float(agreement_amount)))*100
        else:
            agreement_amount = int(agreement_amount)*100
        url = settings.ZAI_URL_ACCOUNT+"/payto/agreements/validate"
        if payid == "none":
            payload = json.dumps({
            "user_external_id": zai_user_id,
            "priority": "ATTENDED",
            "agreement_info": {
                "description": str(description),
                "purpose_code": "OTHR",
                "agreement_type": "AUPM",
                "validity_start_date": start_date,
                "validity_end_date": str(zai_agreement_end_date(start_date)),
                "automatic_renewal": "false",
                "debtor_info": {
                "debtor_account_details": {
                    "account_id_type": "BBAN",
                    "account_id": account_id
                },
                "debtor_details": {
                    "debtor_name": str(name),
                    "debtor_type": "ORGN",
                    "ultimate_debtor_name": str(name)
                }
                },
                "creditor_info": {
                "ultimate_creditor_name": "WidophRemit"
                },
                "payment_initiator_info": {
                "initiator_id": settings.ABN_NO,
                "initiator_id_type_code": "AUBN",
                "initiator_legal_name": "WidophRemit",
                "initiator_name": "WidophRemit"
                },
                "payment_terms": {
                "payment_amount_info": {
                    "currency": "AUD",
                    "type": "VARI"
                },
                "maximum_amount_info": {
                    "amount": agreement_amount,
                    "currency": "AUD"
                },
                "frequency": "ADHOC"
                }
            }
            })
        else:
            payload = json.dumps({
            "user_external_id": zai_user_id,
            "priority": "ATTENDED",
            "agreement_info": {
                "description": str(description),
                "purpose_code": "OTHR",
                "agreement_type": "AUPM",
                "validity_start_date": start_date,
                "validity_end_date": str(zai_agreement_end_date(start_date)),
                "automatic_renewal": "false",
                "debtor_info": {
                "debtor_account_details": {
                    "account_id_type": "PAYID",
                    "payid_details": {
                    "payid_type": payid_type,
                    "payid": payid
                    }
                },
                "debtor_details": {
                    "debtor_name": str(name),
                    "debtor_type": "ORGN",
                    "ultimate_debtor_name": str(name),
                }
                },
                "creditor_info": {
                "ultimate_creditor_name": "WidophRemit",
                },
                "payment_initiator_info": {
                "initiator_id": settings.ABN_NO,
                "initiator_id_type_code": "AUBN",
                "initiator_legal_name": "WidophRemit",
                "initiator_name": "WidophRemit"
                },
                "payment_terms": {
                "payment_amount_info": {
                    "currency": "AUD",
                    "type": "VARI"
                },
                "maximum_amount_info": {
                "amount": str(agreement_amount),
                "currency": "AUD"
                },
                "frequency": "ADHOC"
                }
            }
            })
        headers = {'Authorization': 'Bearer '+access_token,'Content-Type': 'application/json' }
        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return bad_response(str(e)+" in line "+str(exc_tb.tb_lineno))

""" Get Zai Agreement Status """
def zai_get_agreement_status(agreement_id, access_token):
    try:
        url = settings.ZAI_URL_ACCOUNT+"/payto/agreements/"+agreement_id
        headers = {'Authorization': 'Bearer '+access_token  }
        response = requests.request("GET", url, headers=headers)
        response = response.json()
        agreement_status = response['status']
        if agreement_status == "VALIDATION_FAILED":
            return agreement_status
        if agreement_status != 'VALIDATED':
            agreement_status = zai_get_agreement_status(agreement_id, access_token)    
        return agreement_status
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return None
    
""" Create Zai Agreement """
def zai_create_agreement(agreement_uuid, access_token):
    try:
        agreement_status = zai_get_agreement_status(agreement_id=agreement_uuid, access_token=access_token)
        if agreement_status == "VALIDATION_FAILED":
            return agreement_status
        if agreement_status == 'VALIDATED':
            url = settings.ZAI_URL_ACCOUNT+"/payto/agreements/"+agreement_uuid+"/create"
            headers = { 'Authorization': 'Bearer '+access_token }
            agreement_response = requests.request("POST", url, headers=headers)
            agreement_response = agreement_response.json()
            return agreement_response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return None
    
""" Get agreement details """
def zai_get_agreement_details(agreement_uuid,access_token):
    try:
        url = settings.ZAI_URL_ACCOUNT+"/payto/agreements/"+agreement_uuid
        headers = { 'Authorization': 'Bearer '+access_token }
        response = requests.request("GET", url, headers=headers)
        response = response.json()
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return None
    
""" Zai Agreement payment initiate request """
def zai_initiate_payment(access_token, agreement_uuid, send_amount, payment_id, reason):
    try:
        if '.' in str(send_amount):
            send_amount = float(send_amount)*100
        else:       
            send_amount = int(send_amount)*100  
        send_amount = str(send_amount).split('.')
        send_amount = send_amount[0]      
        url = settings.ZAI_URL_ACCOUNT+"/payto/agreements/"+str(agreement_uuid)+"/payment_requests/initiate"
        payload = json.dumps({
        "priority": "ATTENDED",
        "payment_info": {
            "instructed_amount": send_amount,
            "last_payment": False,
            "end_to_end_id": str(payment_id),
            "remittance_info": str(reason),
        }
        })
        headers = {
        'Authorization': 'Bearer '+access_token,
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        print(response, "payment initiate api response ======================")
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return None
    
""" Update agreement """
def zai_update_agreement_status(agreement_uuid, access_token, reason=None):
    if reason is None:
        reason = "New agreement created by debtor"
    try:
        url = settings.ZAI_URL_ACCOUNT+"/payto/agreements/"+str(agreement_uuid)+"/status"
        payload = json.dumps({
        "status": "CANCELLED",
        "reason_code": "REQINTPRTY",
        "reason_description": reason
        })
        headers = { 'Authorization': 'Bearer '+access_token, 'Content-Type': 'application/json' }
        response = requests.request("PATCH", url, headers=headers, data=payload)
        response = response.json()
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return False
    
""" Get supplementary data with zai transaction id from webhook """
def get_zai_supplementary_data(zai_transaction_id, access_token):
    try:
        url = settings.ZAI_URL_ACCOUNT+"/transactions/"+zai_transaction_id+"/supplementary_data"
        headers = { 'Authorization': 'Bearer '+access_token }
        response = requests.request("GET", url, headers=headers)
        response = response.json()
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return None
    
""" Update zai agreement """
def zai_update_agreement(access_token, agreement_uuid, agreement_amount):
    try:
        if '.' in agreement_amount:
            agreement_amount = int(round(float(agreement_amount)))*100
        else:
            agreement_amount = int(agreement_amount)*100         
        url = settings.ZAI_URL_ACCOUNT+"/payto/agreements/"+agreement_uuid+"/amend"
        payload = json.dumps({
        "priority": "ATTENDED",
        "bilateral_amendments": {
            "payment_terms": {
            "payment_amount_info": {
                "currency": "AUD",
                "type": "VARI"
            },
            "maximum_amount_info": {
                "amount": str(agreement_amount),
                "currency": "AUD"
            } }
        }  })
        headers = {'Authorization': 'Bearer '+access_token,'Content-Type': 'application/json' }
        response = requests.request("PATCH", url, headers=headers, data=payload)
        response = response.json()
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return None

################################################ Fraud.Net ################################################
""" Transaction check Api for zai payment gateway """
def zai_fraudnet_tranaction_check(fraudnet_payment_status, recipient_account_number, transaction_id, send_currency, send_amount, payment_id, recipient_id, recipient_country_code, recipient_address, recipient_name, customer_postcode, customer_country_code, customer_dob, customer_mobile, customer_email, customer_id, customer_fn, customer_ln, customer_address, customer_city, customer_state):
    try:
        url = settings.SANDBOX_URL
        send_method = "npp"
        payload = json.dumps({
        "customer": {
            "id": customer_id,
            "first_name": customer_fn,
            "last_name": customer_ln,
            "address1": customer_address,
            "city": customer_city,
            "region": customer_state,
            "postal_code": customer_postcode,
            "country": customer_country_code,
            "dob": customer_dob,
            "phone": customer_mobile,
            "email": customer_email
        },
        "seller": {
            "account_type": "person",
            "seller_id": recipient_id,
            "country": recipient_country_code,
            "address1": recipient_address,
            "name": recipient_name
        },
        "device": {
            "ip_address": str(get_ip())
        },
        "account": {
            "account_id": recipient_account_number
        },
        "payment": {
            "payment_id": transaction_id,  #primary key of transaction table
            "payment_status": "auth",
            "actual_ccy": send_currency,
            "actual_amt": send_amount,
            'method':send_method
        },
        "transaction": {
            "type": "sale",
            "iban": None,
            "ident_country": None,
            "ident_id": None,
            "ident_type": None,
            "order_currency": send_currency,
            "order_discount": None,
            "order_id": payment_id,    #transaction id of payment
            "order_is_digital": False,
            "ordered_on": "now",
            "status": fraudnet_payment_status,
            "total_spent": send_amount,
            "user_id": customer_id,
            "user_locale": customer_country_code
        }
        })
        headers = {
        'Authorization': 'Basic '+settings.FRAUD_TOKEN,
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        CreateTextFile('fraudnet_transaction.txt', response)
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
        error_logs(file_content)
        return bad_response(str(e)+" in line "+str(exc_tb.tb_lineno))
    
""" Update FN data in DB (Transaction AI)"""    
def update_fn_data_in_db(response, customer_id, transaction_id):
    try:
        response_data = response['data']
        risk_score = response_data['risk_score']
        risk_group = response_data['risk_group']
        label = ""
        tm_status = "No action triggered"
        aml_pep_status = "NA"
        rule = "No rule triggered"
        for x in response_data['tags']:
            if 'name' in x:
                if "AML" in x['name']:
                    if x['state'] == "no_match":
                        aml_pep_status = False
                    elif x['state'] == "match" or x['state'] == "matched":
                        aml_pep_status = True
            if 'type' in x:
                if x['type'] == "label":
                    label =  str(label +str(x['name'])+", ")
                    if label.endswith(", "):
                        label = label[:-2]
                    Transaction_details.objects.filter(id=transaction_id).update(tm_label=label)
            if 'action' in x:
                if x['action'] != '' and x['action'] is not None:
                    tm_status = x['action']
                    if str(x['type']).lower() == "rule":
                        rule = str(x['name'])
                else:
                    tm_status = "No action triggered"
        Transaction_details.objects.filter(id=transaction_id).update(rule=rule, risk_score=risk_score, risk_group=risk_group, tm_status=tm_status, aml_pep_status=aml_pep_status)
        payment_status = transaction['pending_payment']
        return payment_status
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

################################################ Referrals / Vouchers ################################################
""" Calculate discount and update discount in DB """
def discount_calculation(transaction_id, discount_amount, update):
    try:
        amt = Transaction_details.objects.filter(transaction_id=transaction_id).values('amount','total_amount')
        if amt[0]['total_amount'] == None or str(amt[0]['total_amount']) == '':
            total_amount = 0
        total_amount = float_int(replace_comma(amt[0]['total_amount']))
        discount_amount = float_int(replace_comma(discount_amount))
        final_amount= float(total_amount) - float(discount_amount)
        final_amount = comma_value(final_amount)
        discount_amount = comma_value(discount_amount)
        total_amount = comma_value(total_amount)
        if update == True:
            Transaction_details.objects.filter(transaction_id=transaction_id).update(total_amount=total_amount, amount = final_amount, discount_amount=discount_amount)
        return {'total_amount':total_amount, 'discount_amount':discount_amount, 'final_amount':final_amount}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return bad_response(str(e)+" in line "+str(exc_tb.tb_lineno))
    
def payment_usage_check(user_id, customer_id, transaction_id):
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
                status = "You transactions limit has been exceeded. Please update your transactions limit from profile section."               
            elif amount_value and amount_value != 'unlimited' and float(total_amount) > float(amount_value):  
                status = "Your transactions amount usage limit has been exceeded. Please update your amount usage limit from profile section." 
        return status
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in payment_app/helpers"
        error_logs(file_content)
        return None   

def CreateErrorFile(file_content):
    file_content = json.dumps(file_content)
    file_name = 'error.txt'
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    with open(file_path, 'a') as text_file:
        text_file.write('\n\n' + "Date: ============>  "+ str(get_current_date()))
        text_file.write('\n\n' + file_content)
    return True

def CreateTextFile(file_name, file_content):
    file_content = json.dumps(file_content)
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    with open(file_path, 'a') as text_file:
        text_file.write('\n\n' + "Date: ============>  "+ str(get_current_date()))
        text_file.write('\n\n' + file_content)
    return True