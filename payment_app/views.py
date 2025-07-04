from Widoph_Remit.package import *
from service_providers.models import *
from auth_app.sendsms import *
from auth_app.views import *
from io import BytesIO
from datetime import datetime
import os
from twilio.rest import Client  
from dateutil import parser
from django.db.models.functions import Concat
from django.db.models import Avg, F, CharField, Value
from .helper import *
import datetime
from datetime import datetime

#stripe 
stripe.api_key = settings.API_SECRET_KEY
stripe.api_version = "2020-08-27"

transaction = settings.TRANSACTION
referral_dict = settings.REFERRALS
zai = settings.ZAI

################################ Recipient Views ################################
class Create_recipient_validation_View(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]   
     
    def post(self,request,format=None):
        bank_name = request.data.get("bank_name")
        account_name = request.data.get("account_name")
        account_number = request.data.get("account_number")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        email = request.data.get("email")
        mobile = request.data.get("mobile")
        flat = request.data.get("flat")
        building = request.data.get("building")
        street = request.data.get("street")
        postcode = request.data.get("postcode")
        city = request.data.get("city")
        state = request.data.get("state")
        country = request.data.get("country")
        reason = request.data.get("reason")
        user_serializer = UserProfileSerializer(request.user)
        user_id = user_serializer.data['id']
        type = request.data.get('type')
        error_dict = {'account name':account_name, 'account number':account_number,'first_name':first_name, 'last_name': last_name, 'email':email, 'mobile':mobile, 'country':country,'reason':reason}
        for k, v in zip(error_dict.keys(), error_dict.values()):
            if v and k == 'email':
                if not '@' in v and not '.' in v:
                    raise serializers.ValidationError({"code":settings.BAD_REQUEST, 'message':'Please enter a valid email address', "Emailinvalid":"Please enter a valid email address"})
                if Recipient.objects.filter(user=user_serializer.data['id'], email=v).exists():
                    raise serializers.ValidationError({"code":settings.BAD_REQUEST, 'message':'email already exists', "emailexist":"email already exists"})
            if v and k == 'mobile':
                if not v.isnumeric():
                    raise serializers.ValidationError({'code':settings.BAD_REQUEST, 'message':'Enter a valid mobile number', 'Entermobile':"Enter a valid mobile number"})
                if len(v) > 15 or len(v) < 7:
                    raise serializers.ValidationError({'code':settings.BAD_REQUEST, 'message':'Enter a valid mobile number', 'Validmobile':"Enter a valid mobile number"})
                if Recipient.objects.filter(user=user_serializer.data['id'], mobile=v).exists():
                    raise serializers.ValidationError({"code":settings.BAD_REQUEST, 'message':'mobile already exists', "mobileexist":"mobile already exists"})
            if not v:
                key = "Enter"+k
                key = key.replace(" ","")
                key = key.replace("_","")
                if k == 'bank_name':
                    raise serializers.ValidationError({'code':settings.BAD_REQUEST, 'message':'Please enter bank name', 'Enterbank':"Please enter bank name."})
                if k == 'country':
                    raise serializers.ValidationError({'code':settings.BAD_REQUEST,'message':"Please select country", 'Selectcountry':"Please select country"})
                if k == 'reason':
                    raise serializers.ValidationError({"code":settings.BAD_REQUEST, 'message':"Please enter reason", "Reason":"Please select reason"})
                raise serializers.ValidationError({"code":settings.BAD_REQUEST, "message":"Please enter "+k, key:"Please enter "+k})     
        if email and Recipient.objects.filter(user=user_id, email=email).exists():
            raise serializers.ValidationError({"code":settings.BAD_REQUEST, 'message':'Email already exist', "Emailexist":"Email already exist"})
        if mobile and Recipient.objects.filter(user=user_id, mobile=mobile).exists():
            raise serializers.ValidationError({"code":settings.BAD_REQUEST, 'message':'Mobile number already exist', "Mobileexist":"Mobile number already exist"})
        recipient_users = Recipient.objects.filter(user=user_id).values('id')
        for x in recipient_users:
            if account_number and Recipient_bank_details.objects.filter(recipient_id=x['id'], account_number=account_number).exists():
                raise serializers.ValidationError({'code':settings.SUCCESS_CODE, 'message':'Recipient with this account number already exist', 'Accountexist':"Recipient with this account number already exist"})
        return Response({'code': settings.SUCCESS_CODE, 'message':settings.SUCCESS_MESSAGE})

""" Recipient's Account Number Validation """
class Recipient_account_number_validation(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]  

    def post(self,request,format=None):
        account_number = request.data.get("account_number")        
        try:
            # if not account_number or str(account_number).strip() == '':
            #     return bad_response("Please enter account number")
            if account_number:
                recipient_users = Recipient.objects.filter(user_id=request.user.id).values('id')
                if is_obj_exists(Recipient_bank_details, {'recipient_id__in':recipient_users, 'account_number':account_number}):
                    return bad_response('Recipient with this account number already exists!')           
            return success_response("success")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

""" Create recipient """
class Recipient_create_View(APIView):
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
            if 'mobile' in payload:
                payload['mobile'] = "+"+str(payload['mobile'])

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
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

""" Get recipients list """    
class Recipient_list_View(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]   
     
    def post(self,request,format=None):
        try:
            serializer = UserProfileSerializer(request.user)
            user_id = request.user.id
            if not is_obj_exists(Recipient, {'user_id':user_id}):
                return bad_response("Recipients not found")
            recipient_data = get_all_filter_values(Recipient, {'user_id':user_id})
            for i in recipient_data:
                if is_obj_exists(Recipient_bank_details, {'recipient_id':i['id']}):
                    bank_data = filter_model_objs(Recipient_bank_details, {'recipient_id':i['id']}, {'bank_name','account_name','account_number'})
                    i.update(bank_data[0])
                    if is_obj_exists(Transaction_details, {'recipient':i['id']}):
                        reason = Transaction_details.objects.filter(recipient=i['id']).values('reason').order_by('-id')
                        i.update(reason=reason[0]['reason'])            
            return success_response("success", data_to_str(recipient_data))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

""" Update, get and delete recipient """  
class Recipient_update_View(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]    

    @csrf_exempt
    def get(self, request, pk, format=None):
        try:
            if not is_obj_exists(Recipient, {'id':pk}):
                return bad_response("Recipient does not exists!")
            data = get_all_filter_values(Recipient, {'id':pk})[0]
            bank = filter_model_objs(Recipient_bank_details, {'recipient':pk}, {'recipient_id','bank_name','account_name','account_number'})
            data.update(bank[0])
            return success_response("success", data_to_str([data])[0])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

    @csrf_exempt
    def post(self, request, pk, format=None):
        middle_name = ''
        flat = ''
        postcode = ''
        email = ''
        email = request.data.get("email")
        middle_name = request.data.get("middle_name")
        flat = request.data.get("flat")
        postcode = request.data.get("postcode")

        try:
            payload = request.data
            user_id = request.user.id
            if not is_obj_exists(Recipient, {'user':user_id, 'id':pk}):
                return bad_response("Recipient does not exists!")   
            RECIPIENT_FIELDS = ['first_name','last_name','mobile','building','street','city','state','country','country_code','bank_name','account_number']
            
            #validation
            for k in RECIPIENT_FIELDS:
                if k in payload and str(k).strip() == '' and k == None:
                    return bad_response("Please enter "+replace_(k))
                
            #account number validation
            r_id = Recipient.objects.filter(user_id=user_id)
            if 'account_number' in payload and is_obj_exists(Recipient_bank_details, {'recipient_id__in':r_id, 'account_number':payload['account_number']}):
                rbank = Recipient_bank_details.objects.filter(recipient_id=pk)
                if str(rbank[0].account_number) != str(payload['account_number']):
                    return bad_response("Account number already exists!")
            
            #concatinating + sign in mobile if not
            if 'mobile' in payload and not "+" in str(payload['mobile']):
                payload['mobile'] = "+"+str(payload['mobile'])

            update_dict = dict(request.data)
            update_dict.update(email=email, middle_name = middle_name, flat = flat, postcode = postcode)

            #updating recipient data
            recipient_obj = Recipient.objects.get(id=pk)
            recipient_serializer = Update_Recipient_Serializer(recipient_obj, data=update_dict, partial=True)
            if recipient_serializer.is_valid():
                recipient_serializer.save()
            data = dict(recipient_serializer.data)

            request.data['account_name'] = data['first_name']+" "+data['last_name']
            #updating recipient bank data
            bank_obj = Recipient_bank_details.objects.get(id=pk)
            bank_serializer = Update_Recipient_Bank_Serializer(bank_obj, data=request.data, partial=True)
            if bank_serializer.is_valid():
                bank_serializer.save()
            data.update(bank_serializer.data)
            return success_response("success", data_to_str([data])[0])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

    @csrf_exempt
    def delete(self, request, pk, format=None):
        try:
            if not is_obj_exists(Recipient, {'id':pk}):
                return bad_response("Recipient does not exists!")
            recipient =  Recipient.objects.get(pk=pk)
            bank = Recipient_bank_details.objects.filter(recipient_id=pk)
            if recipient.delete() and bank.delete():
                return success_response("Recipient deleted successfully")
            return bad_response("Recipient is not deleted")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        

################################ Zai PayId Per User ################################  
""" Create or Get Zai PayID """
class Zai_register_payid_peruser_View(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        profile_serializer = UserProfileSerializer(request.user)        
        zai_user_id = None 
        user_id = request.user.id
        zai_email = request.user.email
        try:
            transaction_id = request.data.get("transaction_id")
            if not transaction_id or str(transaction_id).strip() == '':
                return bad_response("Please enter transaction id") 
            if not is_obj_exists(Transaction_details, {'transaction_id':transaction_id}):
                return bad_response("Invalid transaction id")
            
            #updating payin / send method in DB
            update_model_obj(Transaction_details, {'transaction_id':transaction_id}, {'send_method':zai['payid'], 'updated_at':get_current_datetime(), 'date':get_current_date()})
            
            #get transaction details and checking recipient
            obj = Transaction_details.objects.filter(transaction_id=transaction_id)[0]
            if not obj.recipient:
                return bad_response("Recipient not found for this transaction. Please update recipient")
            
            access_token = zai_token(request)    

            #if payid exists in data then return payid details
            if is_obj_exists(zai_payid_details, {'user_id':user_id}):
                payid_obj = zai_payid_details.objects.filter(user_id=user_id)
                payid_obj = payid_obj[0]
                zai_user_id = payid_obj.zai_user_id
                payid = payid_obj.payid
            else:
                #searching email in zai to get user id if exists
                search_response = zai_search_email_id(access_token=access_token, email=zai_email)
                if 'users' in search_response:
                    result = next((user for user in search_response['users'] if str(user.get('email')).lower() == str(zai_email).lower()), None)
                    if result is not None:
                        zai_user_id = result['id']
                        zai_email = result['email']      

                #creating user in zai   
                if not zai_user_id:
                    user_response = zai_create_user(access_token=access_token, customer_id=request.user.customer_id, email=request.user.email, mobile=request.user.mobile, fn=request.user.First_name, ln=request.user.Last_name)
                    if 'errors' in user_response:
                        error = zai_error(user_response)
                        return bad_response(error)
                    zai_user_id = user_response['users']['id']  
                                  
                #get wallet id of user
                wallet_response =  zai_get_user_wallet(access_token, zai_user_id)
                if 'errors' in wallet_response:
                    return bad_response(wallet_response['errors'])  
                wallet_account_id = wallet_response['wallet_accounts']['id']

                #get virtual account id from wallet account id
                v_list_response = zai_virtual_account_list(access_token, wallet_account_id)
                virtual_account_total = v_list_response['meta']['total']
                if virtual_account_total == 0:

                    #creating virtual account with wallet id
                    virtual_account_response = zai_create_virtual_account(access_token, wallet_account_id)
                    if 'errors' in virtual_account_response:
                        return bad_response(virtual_account_response['errors'])
                    else:
                        virtual_account_id = virtual_account_response['id']
                        virtual_account_number = virtual_account_response['account_number']
                        routing_number = virtual_account_response['routing_number']
                else:
                    virtual_account_id = v_list_response['virtual_accounts'][0]['id']
                    virtual_account_number = v_list_response['virtual_accounts'][0]['account_number']
                    routing_number = v_list_response['virtual_accounts'][0]['routing_number']    

                #registering pay id with virtual account id
                payid = zai_create_payid(request.user.customer_id)
                payid_response =  zai_register_payid_peruser(access_token, virtual_account_id, payid, zai_user_id)
                if 'errors' in payid_response:
                    return bad_response(payid_response['errors'])
                
                #inserting payid details in database
                zai_payid_details.objects.create(user_id=user_id, zai_user_id=zai_user_id, zai_email=zai_email, payid=payid, wallet_account_id=wallet_account_id, bsb_code=routing_number, account_number=virtual_account_number)        
            
            #get ccureent payment status of transaction
            payment_status = Transaction_details.objects.filter(transaction_id=transaction_id).values('payment_status','id')
            return success_response(payment_status[0]['payment_status'], {"payid":payid, "id":payment_status[0]['id'],"transaction_id":transaction_id})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        
""" Zai Payid commit payment view """
class Zai_payid_per_user_payment_View(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        referral_meta_id = None
        user_id = request.user.id
        transaction_id = request.data.get("transaction_id")
        referral_meta_id = request.data.get("referral_meta_id")

        if not transaction_id or str(transaction_id).strip() == '':
            return bad_response("Please enter transaction_id")
        if not is_obj_exists(Transaction_details, {'transaction_id':transaction_id}):
            return bad_response("Invalid transaction_id")
        try:
            if str(referral_meta_id).lower().strip() == "none" or str(referral_meta_id).strip() == '':
                final_amount = 0
            else:
                final_amount = apply_discount(transaction_id, referral_meta_id)
            
            #updating send method
            Transaction_details.objects.filter(transaction_id=transaction_id).update(send_method=zai['payid'], updated_at=get_current_datetime(), date=get_current_date())
            
            user = UserProfileSerializer(request.user)
            access_token = zai_token(request)    

            #updating transaction in database
            tobj = Transaction_details.objects.filter(transaction_id=transaction_id)        
            tobj = tobj[0]  

            #getting payid details
            if zai_payid_details.objects.filter(user_id= user.data['id']).exists():
                payid_obj = zai_payid_details.objects.filter(user_id= user.data['id'])
                payid_obj = payid_obj[0]
                valid = str(payid_obj.bsb_code)+str(payid_obj.account_number)

                #sending money to user wallet in sandbox mode
                if settings.HOST != "LIVE":
                    send_money_response = zai_send_money_to_wallet(transaction_id, access_token, str(tobj.amount), payid_obj.payid, payid_obj.zai_user_id, valid)
                    if send_money_response and 'Message' in send_money_response:
                        return bad_response(send_money_response['Message'])
                    Transaction_details.objects.filter(transaction_id=transaction_id).update(payment_status=transaction['pending_payment'], updated_at=get_current_datetime())

            #get updated transaction data and updating preferred curency pair of user in db
            payment_status =  Transaction_details.objects.filter(transaction_id=transaction_id).values()
            User.objects.filter(id=user_id).update(source_currency=str(payment_status[0]['send_currency']), destination_currency=str(payment_status[0]['receive_currency']))      
            
            #sending notifications to WidophRemit via email and sms 
            if str(payment_status[0]['payment_status']) != str(transaction['pending_review']):
                if Transaction_details.objects.filter(customer_id=user.data['customer_id']).exists():
                    transactions = Transaction_details.objects.filter(customer_id=user.data['customer_id']).count()                    
                    count = User.objects.filter(id=user.data['id']).update(transactions=transactions)

                Transaction_details.objects.filter(transaction_id=transaction_id).update(payment_status=transaction['pending_payment'])
                send_sms_to_RA(type="transaction", data={'payment_status':transaction['pending_payment'],'transaction_id':transaction_id,'customer_id':user.data['customer_id'],'send_currency':tobj.send_currency, 'amount': tobj.amount, 'exchange_rate':tobj.exchange_rate})
                email_to_RA("transaction", transaction_id)
            
            #creating notification for adminpanel
            notification.objects.create(source_id=payment_status[0]['id'], source_type="transaction", source_detail=str(tobj.amount)+" ("+str(tobj.send_currency+")"), message=settings.NOTIFICATION_TRANSACTION_MSG)
            payment_status = Transaction_details.objects.filter(transaction_id=transaction_id).values('payment_status','id','amount')        
            if str(final_amount) == "0":
                final_amount = payment_status[0]['amount']
            return success_response(payment_status[0]['payment_status'], {"id":payment_status[0]['id'],"transaction_id":str(tobj.transaction_id), "final_amount":final_amount})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

""" Get Zai PayId details """
class Zai_payid_detail_View(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            user_id = request.user.id            
            if zai_payid_details.objects.filter(user_id=user_id).exists():
                data = zai_payid_details.objects.filter(user_id=user_id).values('payid','zai_email')
                return success_response("success", data[0])
            else:
                return bad_response(message="No PayID registered")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))


################################ Zai PayTo Agreement ################################  
""" Validate PayID with TELI and EMAIL type for payto agreement """
class Validate_payto_payid_view(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        payid = str(request.data.get("payid")).lower()
        payid_type = str(request.data.get("payid_type")).upper()
        try:
            if not payid or str(payid).strip() == '':
                return bad_response("Please enter payid")
            if not payid_type or str(payid_type).strip() == '':
                return bad_response("Please enter payid_type")
            if payid_type != 'EMAL' and payid_type != 'TELI':
                return bad_response("Invalid payid_type")
            if payid_type == 'EMAL':
                first_name = str(request.user.First_name).lower()
                last_name = str(request.user.Last_name).lower()
                if not first_name in payid and not last_name in payid:
                    return bad_response("PayID must include your First Name or Last Name")
            else:
                mobile = str(request.user.mobile).replace('+61','')
                #remove 0 from both payid and mobile to match both
                if str(mobile[0]) == "0":
                    mobile = mobile[1:]
                if str(payid[0]) == "0":
                    payid = str(payid[1:])
                if mobile != payid:
                    return bad_response("PayID must include your registered mobile number")
            return success_response("success")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
                                                 
""" Create Zai PayTo Agreement """
class Zai_create_payto_agreement_View(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        payid = None
        account_id = None
        bsb = None
        payid = request.data.get("pay_id")
        payid_type = request.data.get("payid_type")
        bsb = request.data.get("bsb")
        account_number = request.data.get("account_number")
        agreement_amount = request.data.get('agreement_amount')
        start_date = request.data.get('start_date')
        try:
            if not payid and not account_number:
                return bad_response("Please enter PayId or account details")
            if payid:
                if not payid_type:
                    return bad_response("Please enter payid_type")
            if account_number:
                if not bsb:
                    return bad_response("Please enter BSB code")
                payid_type = "BBAN"
            if not agreement_amount:
                return bad_response("Please enter agreement amount")
            if not start_date:
                return bad_response("Please enter start_date")

            if str(payid_type).upper() == "TELI":
                payid = "+61-"+str(payid)
                
            access_token = zai_token(request)     
            zai_email = request.user.email
            user_id = request.user.id
            payid = str(payid).lower()
            payid_type = str(payid_type).upper()
            zai_user_id = None

            #search email id in zai
            search_response = zai_search_email_id(access_token, zai_email)
            if 'users' in search_response:
                for i in search_response['users']:
                    if str(i['email']).lower() == str(zai_email).lower():
                        zai_user_id = i['id']
                        zai_email = i['email']
                        break
            
            if zai_user_id == None:
                #creating zai user
                user_response = zai_create_user(access_token=access_token, customer_id=request.user.customer_id, email=request.user.email,  mobile=request.user.mobile, fn=request.user.First_name, ln=request.user.Last_name)
                if 'errors' in user_response:
                    error = zai_error(user_response)
                    return bad_response(error)                
                zai_user_id = user_response['users']['id']
            
            #validate agreement
            if str(payid).lower() == "none":
                account_id = str(bsb)+str(account_number)
            validate_agreement_response = zai_validate_payto_agreement(fn=request.user.First_name, ln=request.user.Last_name, payid_type=payid_type, user_email=request.user.email,access_token=access_token, zai_user_id=zai_user_id, payid=payid, start_date=str(start_date), account_id=account_id, agreement_amount=agreement_amount )
            if 'errors' in validate_agreement_response:
                return bad_response(validate_agreement_response['errors'])
            agreement_uuid = validate_agreement_response['agreement_uuid']
            agreement_status = validate_agreement_response['status']

            #create agreement
            agreement_response = zai_create_agreement(agreement_uuid, access_token)
            if agreement_status == "VALIDATION_FAILED":
                return bad_response(agreement_response)
            if 'errors' in agreement_response:
                return bad_response(agreement_response['errors'])

            #save agreement details in DB
            validity_end_date = zai_agreement_end_date(start_date)  
            if zai_agreement_details.objects.filter(user_id=user_id).exists():
                zai_agreement_details.objects.filter(user_id=user_id).update(zai_user_id=zai_user_id, zai_email=zai_email, status=str(agreement_status).lower(), payid=payid, payid_type=str(payid_type).upper(), agreement_start_date=start_date, account_number=account_number, wallet_account_id=None, bsb_code=bsb, agreement_uuid=agreement_uuid, max_amount=agreement_amount, agreement_end_date=str(validity_end_date))
            else:
                zai_agreement_details.objects.create(user_id=user_id, status=str(agreement_status).lower() ,zai_user_id=zai_user_id, zai_email=zai_email, payid=payid, payid_type=str(payid_type).upper(), agreement_start_date=start_date, agreement_end_date=str(validity_end_date), account_number=account_number, wallet_account_id=None, bsb_code=bsb, agreement_uuid=agreement_uuid, max_amount=agreement_amount)
            return success_response("Agreement has been created successfully. Please authorise it.", {"agreement_uuid":agreement_uuid})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
           
""" Zai PayTo Agreement Payment View """
class Zai_payto_agreement_payment_View(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        referral_meta_id = None
        transaction_id = request.data.get("transaction_id")
        referral_meta_id = request.data.get("referral_meta_id")
        agreement_uuid = request.data.get("agreement_uuid")

        if not agreement_uuid:
            return bad_response("Please enter agreement_uuid")
        if not transaction_id:
            return bad_response("Please enter transaction_id")
        try:
            profile_serializer = UserProfileSerializer(request.user)
            user_id = request.user.id
            access_token = zai_token(request)     
            zai_email = request.user.email
            payment_id = None

            if str(referral_meta_id).lower().strip() == "none" or str(referral_meta_id).strip() == '':
                final_amount = 0
            else:
                final_amount = apply_discount(transaction_id, referral_meta_id)
            if not Transaction_details.objects.filter(transaction_id=transaction_id).exists():
                return bad_response("Invalid transaction_id")
            
            #updating payin method in DB
            Transaction_details.objects.filter(transaction_id=transaction_id).update(send_method=zai['payto'], updated_at=get_current_datetime(), date=get_current_date())
            obj = Transaction_details.objects.filter(transaction_id=transaction_id)
            obj = obj[0]
            if not obj.recipient:
                return bad_response("Recipient not found for this transaction")
            
            #get agreement details
            if not zai_agreement_details.objects.filter(user_id=user_id, agreement_uuid=agreement_uuid).exists():
                return bad_response("Invalid agreement_uuid")
            agreement_details = zai_get_agreement_details(agreement_uuid, access_token)
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

            #updating payment status in DB
            if str(agreement_status).lower() != "active":                
                Transaction_details.objects.filter(transaction_id=transaction_id).update(payment_status=transaction['pending_payment'])
                return Response({"code":"400","message":transaction['pending_payment'], "data":{"id":obj.id,"transaction_id":obj.transaction_id, 'final_amount':str(obj.amount)}})
                # return Response({"code":"400","message":"Please authorise your agreement.", "data":{"id":obj.id,"transaction_id":obj.transaction_id, 'final_amount':str(obj.amount)}})
            else:
                Transaction_details.objects.filter(transaction_id=transaction_id).update(payment_status=transaction['pending_payment'])
                zai_agreement_details.objects.filter(user_id=user_id, agreement_uuid=agreement_uuid).update(status='active')

            #recipient bank details
            if not Recipient.objects.filter(id=obj.recipient).exists():
                return bad_response("Invalid recipient")
            recipient = Recipient.objects.filter(id=obj.recipient)
            recipient = recipient[0]
            if Recipient_bank_details.objects.filter(recipient_id=obj.recipient).exists():
                bank = Recipient_bank_details.objects.filter(recipient_id=obj.recipient)
                bank = bank[0]

            if User_address.objects.filter(user_id=user_id).exists():
                address = User_address.objects.filter(user_id=user_id)
                address = address[0]

            #payment initiate request
            initiate_response = zai_initiate_payment(access_token=access_token, agreement_uuid=agreement_uuid, send_amount=str(obj.amount), payment_id=transaction_id, reason=obj.reason)
            print(initiate_response, 'initiate_response ==================>')
            if 'errors' in initiate_response:
                return bad_response(initiate_response['errors'])
            
            if Transaction_details.objects.filter(customer_id=request.user.customer_id).exists():
                transactions = Transaction_details.objects.filter(customer_id=request.user.customer_id).count()                    
                count = User.objects.filter(id=user_id).update(transactions=transactions)
                
            #Fraudnet transaction check api
            fraudnet_payment_status="approved" 
            fraudnet_response = zai_fraudnet_tranaction_check(fraudnet_payment_status, recipient_account_number = str(bank.account_number), transaction_id= str(obj.id), send_currency=str(obj.send_currency), send_amount=str(obj.amount),  payment_id=str(transaction_id), recipient_id=str(obj.recipient),recipient_country_code = str(recipient.country_code), recipient_address= str(recipient.building+" "+recipient.street+" "+recipient.city+" "+recipient.state), recipient_name = str(recipient.first_name+" "+recipient.last_name), customer_postcode = address.postcode, customer_country_code = address.country_code, customer_dob = str(profile_serializer.data['Date_of_birth']) ,customer_mobile = str(profile_serializer.data['mobile']), customer_email = str(profile_serializer.data['email']), customer_id = str(profile_serializer.data['customer_id']), customer_fn = str(profile_serializer.data['First_name']), customer_ln = str(profile_serializer.data['Last_name']), customer_address=str(address.building+" "+address.street+" "+address.city+" "+address.state), customer_city = address.city,customer_state= address.state)
            
            #updating fraudnet data in DB 
            if 'data' in fraudnet_response:
                update_fn_data_in_db(response=fraudnet_response, customer_id=profile_serializer.data['customer_id'], transaction_id=obj.id)
            
            payment_status =  Transaction_details.objects.filter(transaction_id=transaction_id).values()
            #updating curreny pair in user table and creating notification for adminpanel
            User.objects.filter(id=request.user.id).update(source_currency=str(payment_status[0]['send_currency']), destination_currency=str(payment_status[0]['receive_currency']))      
            notification.objects.create(source_id=payment_status[0]['id'], source_type="transaction", source_detail=str(obj.amount)+" ("+str(obj.send_currency)+")", message=NOTIFICATION_TRANSACTION_MSG)
            
            #sending notification sms and email to WidophRemit 
            send_sms_to_RA(type="transaction",data={'payment_status':payment_status[0]['payment_status'],'transaction_id':transaction_id,'customer_id':profile_serializer.data['customer_id'],'send_currency':obj.send_currency, 'amount': obj.amount, 'exchange_rate':obj.exchange_rate})
            email_to_RA(type="transaction", id=transaction_id)

            #sending transaction email receipt and sms to customer
            email_transaction_receipt(type="create_transaction", transaction_id=transaction_id)
            send_sms_to_customer(type= "customer",data={'transaction_id':transaction_id,'send_currency':obj.send_currency, 'send_amount':obj.amount}, user_mobile=profile_serializer.data['mobile'])
            
            #fetching discounted amount to return in response
            if str(final_amount) == "0":
                final_amount = payment_status[0]['amount']
            return success_response(message=payment_status[0]['payment_status'], data={"id":payment_status[0]['id'],"transaction_id":str(transaction_id), "final_amount":final_amount})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

""" Agreements list of user """
class Zai_list_agreement_View(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            data = None
            send_amount = request.data.get('send_amount')
            user_id = request.user.id
            
            if zai_agreement_details.objects.filter(user_id=user_id, status='active').exists():
                data = zai_agreement_details.objects.filter(user_id=user_id, status='active').values('payid','payid_type','agreement_start_date','agreement_end_date','account_number','bsb_code','max_amount','status','agreement_uuid')
            elif zai_agreement_details.objects.filter(user_id=user_id).exclude(Q(status='cancelled') | Q(status="canceled")).exists():
                data = zai_agreement_details.objects.filter(user_id=user_id).exclude(Q(status='cancelled') | Q(status="canceled")).values('payid','payid_type','agreement_start_date','agreement_end_date','account_number','bsb_code','max_amount','status','agreement_uuid')
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
                if str(data['payid_type']) == "TELI":
                    if "+61-" in str(data['payid']):
                        payid_value = str(data['payid']).replace("+61-","")     
                        data["payid"] = payid_value
                        
                if data['status'] != "active" and data['status'] != 'cancelled' and data['status'] != 'canceled':
                    return success_response("Please authorise agreement.", data)    
                return success_response("success", data)          
            elif zai_agreement_details.objects.filter(Q(status='canceled') | Q(status='cancelled'), user_id=user_id).exists():
                data = zai_agreement_details.objects.filter(Q(status='canceled') | Q(status='cancelled'), user_id=user_id).values()
                if data[0]['agreement_end_date'] is not None:
                    if dateformat(data[0]['agreement_end_date']) < dateformat(datetime.today().date()):
                        return Response({"code": "400", 'expired': True, "message": "Your agreement validity period has been expired. Please create new agreement."})
                return Response({"code": "400", 'expired': False, "message": "Agreement has not been created."})
            else:
                return Response({"code": "400", 'expired': False, "message": "Agreement has not been created."})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

""" Update Agreement """
class Zai_update_agreement_View(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            validity_end_date = None
            agreement_amount = request.data.get('agreement_amount')
            agreement_uuid = request.data.get('agreement_uuid')
            if not agreement_amount:
                return bad_response("Please enter agreement amount")
            if not agreement_uuid:
                return bad_response("Please enter agreement_uuid")

            access_token = zai_token(request)     
            zai_email = request.user.email
            send_currency = "AUD"
            
            if not is_obj_exists(zai_agreement_details, {'zai_email':zai_email, 'agreement_uuid':agreement_uuid}):
                return bad_response("Invalid agreement_uuid")
            
            update_response = zai_update_agreement(access_token, agreement_uuid, agreement_amount)
            zai_agreement_details.objects.filter(zai_email=zai_email, agreement_uuid=agreement_uuid).update(agreement_end_date=validity_end_date, agreement_uuid=agreement_uuid, max_amount=agreement_amount, status="pending_amendment_authorisation")
            
            if 'errors' in update_response:
                return bad_response(update_response['errors'][0]['error_message'])     
            return success_response("Agreement has been updated. Please authorise it.", {"agreement_uuid":agreement_uuid})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
    
""" Search user email in list of zai users """
class zai_search_email_for_agreement_view(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            profile_serializer = UserProfileSerializer(request.user)
            access_token = zai_token(request)     
            zai_email = request.user.email
            zai_user_id = None

            #searching email from zai
            search_response = zai_search_email_id(access_token, zai_email)
            if 'users' in search_response:
                for i in search_response['users']:
                    if str(i['email']).lower() == str(zai_email).lower():
                        zai_user_id = i['id']
                        zai_email = i['email']
                        break
            
            if zai_user_id == None:
                #creating zai user
                user_response = zai_create_user(access_token=access_token, customer_id=request.user.customer_id, email=request.user.email,  mobile=request.user.mobile, fn=request.user.First_name, ln=request.user.Last_name)
                if 'errors' in user_response:
                    error = zai_error(user_response)
                    return bad_response(error)       
                zai_user_id = user_response['users']['id']
            return success_response("success", {"zai_user_id":zai_user_id})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        
################################ Zai Webhooks ################################  
""" Zai Webhook For Transaction """
class zai_transaction_webhook_View(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        if request.method == 'POST':
            try:
                access_token = zai_token(request)   
                payment_id = None
                amount_matched = False
                body_data = request.body
                body_data_json = json.loads(body_data)
                
                file_name = 'transaction_webhooks.txt'
                CreateTextFile(file_name, body_data_json)
                success_logs(body_data_json)
                if body_data_json['transactions']['debit_credit'] == "debit":
                    print(" =================GK Transaction webhook 2 DEBIT ====================")
                    print("body_data 1 ======== ",body_data)

                if body_data_json['transactions']['debit_credit'] == "credit":
                    print(" =================GK Transaction webhook 1 CREDIT ====================")
                    print("body_data 1 ======== ",body_data)
                    zai_transaction_id = body_data_json['transactions']['id']  
                    zai_user_id = body_data_json['transactions']['user_id']
                    
                    if zai_user_id and User.objects.filter(customer_id=zai_user_id).exists():
                        transactions_object = User.objects.filter(customer_id=zai_user_id).values('transactions')
                        if transactions_object[0]['transactions'] is not None:
                            total_transactions = int(transactions_object[0]['transactions'])+1
                            User.objects.filter(customer_id=zai_user_id).update(transactions=total_transactions)

                    #get data with transaction id from supplementary api
                    supplementary_response = get_zai_supplementary_data(zai_transaction_id, access_token)
                    print(supplementary_response, "supplementary_response ==============")
                    if "agreement_uuid" in supplementary_response['npp_details']:
                        payment_id = supplementary_response['npp_details']['end_to_end_id']
                        new_t_data = Transaction_details.objects.filter(transaction_id=payment_id).values()[0]
                        item_response = zai_create_item(seller_id=None, access_token=access_token, payment_id=payment_id, amount_reason=new_t_data['reason'], send_amount=str(new_t_data['amount']), zai_user_id=zai_user_id, send_currency="AUD")
                        print(item_response, "agreement item created =====", payment_id)     
                    else:  
                        #for payid per user
                        if settings.HOST == "LIVE":
                            payment_id = supplementary_response['npp_details']['end_to_end_id']
                            if payment_id == "NOTPROVIDED" or payment_id == "":
                                payment_id = supplementary_response['remittance_information']
                        else:
                            payment_id = supplementary_response['remittance_information']
                        
                        print(payment_id, " =========== payment id 1 ==============")
                        if not Transaction_details.objects.filter(transaction_id=payment_id).exists():
                            print("Transaction exists with payment status processed or does not exists with payment id ====== ")
                            
                            #print all payment status of customer transactions:
                            payment_status_data = Transaction_details.objects.filter(Q(send_method="zai_payid_per_user") | Q(send_method="PayID"), customer_id= zai_user_id).values('transaction_id','payment_status','date')
                            for p in payment_status_data:
                                print("Transactions of user for zai payid peruser  =====>", p['transaction_id'], p['payment_status'], p['date'])

                            amount = str(body_data_json['transactions']['amount'])
                            if Transaction_details.objects.filter(Q(send_method="zai_payid_per_user") | Q(send_method="PayID"), customer_id= zai_user_id, payment_status=transaction['pending_payment']).exists():
                                print("Transaction exists with pending payment status =======> ", zai_user_id)
                                t_data = Transaction_details.objects.filter(Q(send_method="zai_payid_per_user") | Q(send_method="PayID"), customer_id= zai_user_id, payment_status=transaction['pending_payment']).values('transaction_id','amount','payment_status','date')
                                for i in t_data:
                                    if '.' in str(i['amount']):
                                        t_amount = float(i['amount'])*100
                                    else:       
                                        t_amount = int(i['amount'])*100
                                        print("matching webhook amount with database amount =====", t_amount)
                                    if float(t_amount) == float(amount):
                                        amount_matched = True
                                        print("amount matched =======>", float(t_amount) , float(amount))
                                        payment_id = i['transaction_id']
                                        break
                                if not amount_matched:
                                    print("amount not matched so fetching transaction with incomplete status ====")
                                    t_data = Transaction_details.objects.filter(Q(send_method="zai_payid_per_user") | Q(send_method="PayID"), customer_id= zai_user_id, payment_status=transaction['incomplete'], updated_at__date=timezone.now().date()).values('transaction_id','amount','payment_status','date')
                                    print("Transaction exists with incomplete payment status =======> ", zai_user_id)
                                    for i in t_data:
                                        if '.' in str(i['amount']):
                                            t_amount = float(i['amount'])*100
                                        else:       
                                            t_amount = int(i['amount'])*100
                                            print("matching webhook amount with database amount =====", t_amount)
                                        if float(t_amount) == float(amount):
                                            amount_matched = True
                                            print("amount matched =======>", float(t_amount) , float(amount))
                                            payment_id = i['transaction_id']
                                            break
                        if Transaction_details.objects.filter(transaction_id=payment_id).exists():                           
                            print("transaction exists ----------- ")
                            tobj = Transaction_details.objects.filter(transaction_id=payment_id)
                            tobj = tobj[0]

                            #get sender address details
                            user = User.objects.filter(customer_id=tobj.customer_id)
                            user = user[0]
                            if User_address.objects.filter(user_id=user.id).exists():
                                address = User_address.objects.filter(user_id=user.id)                                
                                address = address[0]
                            if Recipient.objects.filter(id=tobj.recipient).exists():
                                robj = Recipient.objects.filter(id=tobj.recipient)
                                robj = robj[0]

                            if Recipient_bank_details.objects.filter(recipient_id=tobj.recipient).exists():
                                bank = Recipient_bank_details.objects.filter(recipient_id=tobj.recipient)
                                bank = bank[0] 
                            fraudnet_response = zai_fraudnet_tranaction_check(fraudnet_payment_status="approved", recipient_account_number = str(bank.account_number), transaction_id= str(payment_id), send_currency=str(tobj.send_currency), send_amount=str(tobj.amount),  payment_id=str(payment_id), recipient_id=str(robj.id),recipient_country_code = str(robj.country_code), recipient_address= str(robj.building+" "+robj.street+" "+robj.city+" "+robj.state), recipient_name = str(robj.first_name+" "+robj.last_name), customer_postcode = address.postcode, customer_country_code = address.country_code, customer_dob = str(user.Date_of_birth) ,customer_mobile = str(user.mobile), customer_email = str(user.email), customer_id = str(user.customer_id), customer_fn = user.First_name, customer_ln = user.Last_name, customer_address=str(address.building+" "+address.street+" "+address.city+" "+address.state), customer_city = address.city,customer_state= address.state)
                            print(fraudnet_response, "fraudnet_response ===================>")
                            if 'data' in fraudnet_response:
                                payment_status = update_fn_data_in_db(response=fraudnet_response, customer_id=user.customer_id, transaction_id=tobj.id)
                                   
                            print("creating item") #have to check item exists or not ===================
                            item_response = zai_create_item(seller_id=None, access_token=access_token, payment_id=payment_id, amount_reason=tobj.reason, send_amount=str(tobj.amount), zai_user_id=zai_user_id, send_currency="AUD")
                            if 'errors' in item_response:
                                item_status = zai_get_item(payment_id, access_token)
                                if str(item_status).lower() == "pending":
                                    amount = Transaction_details.objects.filter(transaction_id=payment_id).values('amount')
                                    zai_update_item(send_amount=str(amount[0]['amount']), payment_id=payment_id, access_token=access_token)
                            print(item_response, "item created")
                    
                    #for agreement and PayId
                    if Transaction_details.objects.filter(transaction_id=payment_id).exists():
                        # ======= getting wallet id
                        wallet_response = zai_get_user_wallet(access_token=access_token, zai_user_id=zai_user_id)
                        if 'errors' in wallet_response:
                            return bad_response(message = wallet_response['errors'])  
                        wallet_account_id = wallet_response['wallet_accounts']['id']

                        payment_response = zai_make_payment(item_id=payment_id, wallet_account_id=wallet_account_id, access_token=access_token)
                        print(payment_response, "payment_response ============")
                        if 'errors' in payment_response:
                            print(payment_response['errors'])
                            item_status = zai_get_item(payment_id, access_token)
                            if str(item_status).lower() == "completed":
                                Transaction_details.objects.filter(transaction_id=payment_id).update(payment_status=transaction['pending_review'] ,payment_gateway_transaction_id=zai_transaction_id,   updated_at = get_current_datetime(), date=get_current_date())   
                        else:
                            print("payment_done for ", payment_id)
                            Transaction_details.objects.filter(transaction_id=payment_id).update(payment_status=transaction['pending_review'] ,payment_gateway_transaction_id=zai_transaction_id,   updated_at = get_current_datetime(), date=get_current_date())   
                        pobj = Transaction_details.objects.filter(transaction_id=payment_id)
                        print("sending sms for payment status changed")
                        if str(pobj[0].send_method) == "zai_payid_per_user" or str(pobj[0].send_method) == "PayID":
                            if User.objects.filter(customer_id=pobj[0].customer_id, is_superuser=False).exists():
                                user_obj = User.objects.filter(customer_id=pobj[0].customer_id, is_superuser=False)
                            if str(pobj[0].payment_status) == transaction['incomplete']: 
                                Transaction_details.objects.filter(transaction_id=payment_id).update(payment_status=transaction['pending_payment'],  updated_at = get_current_datetime(), date= get_current_date())                            
                                send_sms_to_RA(type="transaction",data={'payment_status':transaction['pending_payment'],'transaction_id':pobj[0].transaction_id,'customer_id':pobj[0].customer_id,'send_currency':pobj[0].send_currency, 'amount': pobj[0].amount, 'exchange_rate':pobj[0].exchange_rate})
                                email_to_RA("transaction", payment_id)
                            else:
                                send_sms_to_RA_transaction_webhook(type="transaction_webhook",data={'transaction_id':payment_id,'payment_status':pobj[0].payment_status,'customer_id':pobj[0].customer_id,'send_currency':pobj[0].send_currency.upper(), 'amount': str(pobj[0].amount), 'exchange_rate':pobj[0].exchange_rate})
                                print("sending email  for payment status changed")
                                email_to_RA("webhook_transaction", payment_id)
                            #sending transaction email receipt to customer
                            verified = User.objects.filter(customer_id=pobj[0].customer_id, is_superuser=False).values('is_verified','mobile','First_name','Last_name')
                            email_transaction_receipt(type="create_transaction",transaction_id=payment_id)
                            send_sms_to_customer(type= "customer",data={'transaction_id':payment_id,'send_currency':pobj[0].send_currency, 'send_amount':pobj[0].amount}, user_mobile=verified[0]['mobile'])
                        else:                            
                            send_sms_to_RA_transaction_webhook(type="transaction_webhook",data={'transaction_id':payment_id,'payment_status':pobj[0].payment_status,'customer_id':pobj[0].customer_id,'send_currency':pobj[0].send_currency.upper(), 'amount': str(pobj[0].amount), 'exchange_rate':pobj[0].exchange_rate})
                            verified = User.objects.filter(customer_id=pobj[0].customer_id, is_superuser=False).values('is_verified','mobile','First_name','Last_name')
                            status = Transaction_details.objects.filter(transaction_id=payment_id)         
                            email_to_RA("webhook_transaction", payment_id)                 
                        return success_response(message=str(pobj[0].payment_status), data=None)  
                return success_response(message=transaction['pending_review'], data=None)      
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
                CreateErrorFile(file_content)
                error_logs(file_content)
                return bad_response(str(e)+" in line "+str(exc_tb.tb_lineno))
        else:
            return bad_response("POST method allowed")

""" Zai Create Agreement Webhook """
class zai_agreement_webhook_View(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        if request.method == 'POST':
            try:       
                body_data = request.body
                body_data_json = json.loads(body_data)

                file_name = 'agreement_webhooks.txt'
                CreateTextFile(file_name, body_data_json)
                success_logs(body_data_json)

                print("body_data 1 ==========",body_data_json)
                data = body_data_json['data']
                agreement_status = data['status']
                agreement_uuid = data['agreement_uuid']
                zai_user_id = data['user_external_id']
                agreement_id = data['agreement_info']['agreement_id']
                access_token = zai_token(request)    

                #updating agreement status
                if is_obj_exists(zai_agreement_details, {'agreement_uuid':agreement_uuid}):
                    zai_agreement_details.objects.filter(agreement_uuid=agreement_uuid).update(agreement_id=agreement_id, status= str(agreement_status).lower())
                return success_response(message=transaction['pending_payment'], data=None)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
                CreateErrorFile(file_content)
                error_logs(file_content)
                return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        else:
            return bad_response("POST method allowed")
     
""" Zai PayTo Agreement Payment Initiation Webhook """
class zai_payto_payment_webhook_View(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        if request.method == 'POST':
            try:       
                print("============ agreement payment webhook 1 =======")
                access_token = zai_token(request)     
                body_data = request.body
                body_data_json = json.loads(body_data)

                file_name = 'payment_initiate_webhook.txt'
                CreateTextFile(file_name, body_data_json)
                success_logs(body_data_json)

                print("body_data", body_data_json)
                reason = "None"
                
                #if payment initiation request completed
                if 'event_type' in body_data_json:
                    if str(body_data_json['event_type']) == "PAYMENT_INITIATION_COMPLETED":
                        access_token = zai_token(request)     
                        agreement_uuid = body_data_json['data']['agreement_uuid']
                        payment_id =  body_data_json['original_request']['payment_info']['end_to_end_id']
                        send_currency = "AUD"
                    
                        #get zai user id from DB with agreement uuid
                        if zai_agreement_details.objects.filter(agreement_uuid=agreement_uuid).exists():
                            zai_user_id = zai_agreement_details.objects.filter(agreement_uuid=agreement_uuid).values('zai_user_id')
                            zai_user_id = zai_user_id[0]['zai_user_id']

                        #updating agreement id in transactions table
                        obj = Transaction_details.objects.filter(transaction_id=payment_id).values('transaction_id')
                        if is_obj_exists(Transaction_details, {'transaction_id':payment_id}):
                            Transaction_details.objects.filter(transaction_id=payment_id).update(agreement_id=agreement_uuid)
                            transaction_obj = Transaction_details.objects.filter(transaction_id=payment_id).values('reason','amount')
                            reason = transaction_obj[0]['reason']          
                            send_amount = transaction_obj[0]['amount']     

                            #creating item in zai
                            # item_response = zai_create_item(seller_id=None, access_token=access_token, payment_id=payment_id, amount_reason=reason, send_amount=str(send_amount), zai_user_id=zai_user_id, send_currency="AUD")
                            # print(item_response, "item created =====", payment_id)                       
                        return success_response(message=transaction['pending_payment'], data={"payment_id":str(payment_id)})
                return success_response(message=transaction['pending_payment'], data=None)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
                CreateErrorFile(file_content)
                error_logs(file_content)
                return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        else:
            return bad_response("POST method allowed")
     
################################ Transactions ################################  
""" Create and Update Transaction """
class Create_Update_Transaction_View(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]  

    def post(self, request, format=None):
        transaction_id = request.data.get("transaction_id")
        amount = request.data.get("amount")
        recipient_id = request.data.get("recipient_id")
        
        try:
            user_serializer = UserProfileSerializer(request.user)
            customer_id = user_serializer.data['customer_id']

            if not transaction_id and not amount:
                return bad_response("Please enter transaction_id or amount details.")  
                       
            if transaction_id:
                if not Transaction_details.objects.filter(transaction_id=transaction_id, customer_id=customer_id).exists():
                    return bad_response("Invalid transaction_id")             
                if amount:
                    Transaction_details.objects.filter(transaction_id=transaction_id).update(platform="web", receive_method=str(amount['receive_method']), payout_partner = str(amount['payout_partner']), send_currency=str(amount['send_currency']).upper(), total_amount=amount['send_amount'], amount=amount['send_amount'], receive_amount= str(amount['receive_amount']), receive_currency=str(amount['receive_currency']).upper(), reason=amount['reason'], exchange_rate=amount['exchange_rate'], updated_at = get_current_datetime())       
                if recipient_id:
                    if not Recipient.objects.filter(id=recipient_id, user_id=user_serializer.data['id']).exists():
                        return bad_response(message="Recipient does not exists!")
                    name = Recipient.objects.filter(id=recipient_id).values('first_name','last_name')
                    recipient_name = str(name[0]['first_name'])+" "+str(name[0]['last_name'])
                    Transaction_details.objects.filter(transaction_id=transaction_id).update(platform="web", recipient_name=recipient_name,recipient=recipient_id,  risk_score="NA", risk_group="NA",tm_status="NA", tm_label = "NA")       
            else:
                transaction_data = Transaction_details.objects.create(platform="web", payment_status=transaction['incomplete'], receive_method=str(amount['receive_method']), payout_partner = str(amount['payout_partner']) ,risk_score="NA", risk_group="NA", tm_status="NA", tm_label = "NA",  customer_id=customer_id, send_currency=str(amount['send_currency']).upper(), receive_amount= str(amount['receive_amount']), receive_currency=str(amount['receive_currency']).upper(), reason=amount['reason'], exchange_rate=amount['exchange_rate'], total_amount = amount['send_amount'], amount=amount['send_amount'], updated_at = get_current_datetime())       
                tid = str(getattr(transaction_data, 'id'))   
                transaction_id = create_payment_id(transaction_id=tid)
                Transaction_details.objects.filter(id=tid).update(platform="web", transaction_id=transaction_id) 

            #check transactions account usage limit
            # resposne =  payment_usage_check(request.user.id, request.user.customer_id, transaction_id)
            # if resposne:
            #     return bad_response(resposne)
            return success_response("success", {'transaction_id':transaction_id})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        
""" Transaction History of User """
class transaction_history(APIView):
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
        return success_response("success", {'total_amount':comma_value(total_amount['total']), 'final_amount':comma_value(final_amount['total']),'discount_amount':comma_value(discount_amount['total']), 'data':queryset})
          
""" Single Transaction Summary """
class transaction_summary(APIView):
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
        return success_response("success", dict)

""" No of Completed Transaction and Amount Usage Left """
class Transactions_usage_deatils_View(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]  

    def post(self, request, format=None):
        transactions_left = 0
        amount_left = 0
        unlimited = False
        try:
            count = Transaction_details.objects.filter(Q(payment_status=transaction['completed']) | Q(payment_status=transaction['pending_review']), customer_id=request.user.customer_id).count()
            amount = Transaction_details.objects.filter(Q(payment_status=transaction['completed']) | Q(payment_status=transaction['pending_review']), customer_id=request.user.customer_id).aggregate(total=Sum('total_amount'))
            total_amount = amount['total']
            payment_per_annum = request.user.payment_per_annum
            value_per_annum = request.user.value_per_annum

            print(payment_per_annum, "payment_per_annum")

            count_value = next((item[key] for item in PAYMENT_PER_ANNUM_LIST for key in item if str(payment_per_annum).lower().strip() == key.lower().strip()), None)
           
            print(count_value, "count value  ")
            amount_value = next((item[key] for item in VALUE_PER_ANNUM_LIST for key in item if str(value_per_annum).lower().strip() == key.lower().strip()), None)
            print(count_value, amount_value, "count_value ------- amount_value")
            print(count, amount, "count ==== amount ")
            if count != 0:              
                if count_value == 'unlimited':
                    unlimited = True
                    transactions_left = None
                else:
                    transactions_left = abs(int(count) - int(count_value))
            else:
                if count_value != 'unlimited':
                    transactions_left = count_value
                else:
                    unlimited = True
                    transactions_left = count_value

            if total_amount:
                if amount_value and amount_value == 'unlimited':
                    unlimited = True
                    amount_left = None
                else:
                    amount_left = abs(float(total_amount) - float(amount_value))
            else:
                if amount_value == 'unlimited':
                    unlimited = True
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
        


################################ Veriff Webhook ################################  
""" Veriff Webhook """
class Veriff_webhook_View(APIView):

    def post(self, request, format=None):
        first_name=None
        last_name=None
        id_type=None
        id_number=None
        id_country=None
        ip=None
        status="pending"
        session_id=None
        reason=None
        doc_valid_from=None
        doc_valid_until=None
        state=None
        dob=None
        gender=None
        body_data = request.body
        response = json.loads(body_data)

        CreateTextFile('veriff_webhook.txt', response)
        success_logs(response)

        customer_id = None
        print("veriff webhook response ==========",response)
        if 'vendorData' in response and 'action' in response:
            customer_id = response['vendorData']
        if 'action' in response and str(response['action']).lower() == "submitted":
            status = str(response['action']).lower()
        if 'verification' in response:
            if 'vendorData' in response['verification']:
                print("vendor data exists")
                customer_id = response['verification']['vendorData']
            # status = response['verification']['status']

            print("veriff webhook status ==========", status)
            customer_id = response['verification']['vendorData']
            first_name = response['verification']['person']['firstName']
            last_name = response['verification']['person']['lastName']
            id_type = response['verification']['document']['type']
            id_number = response['verification']['document']['number']
            id_country = response['verification']['document']['country']
            ip = response['technicalData']['ip']
            status = response['verification']['status']
            session_id = response['verification']['id']
            reason = response['verification']['reason']
            doc_valid_from = response['verification']['reason']
            doc_valid_until = response['verification']['reason']
            state = response['verification']['reason']
            dob = response['verification']['person']['dateOfBirth']
            gender = response['verification']['person']['gender']
            # if identity data exists then passing data to application AI FN            
            if str(status).lower() == "approved":
                status = "submitted"
                application = application_check(customer_id, id_number, id_country, id_type, status)   
        if User.objects.filter(customer_id=customer_id).exists():
            User.objects.filter(customer_id=customer_id, is_superuser=False).update(is_digital_Id_verified=str(status).lower())
        print("veriff webhook status ==========", status)
        if 'technicalData' in response:
            ip = response['technicalData']['ip']
        if not Veriff.objects.filter(customer_id=customer_id).exists():
            Veriff.objects.create(customer_id=customer_id, first_name=first_name,last_name=last_name, id_type=id_type, id_number=id_number,id_country=id_country, ip=ip, session_id=session_id, reason=reason, doc_valid_from=doc_valid_from, doc_valid_until=doc_valid_until, state=state, dob=dob, gender=gender)
        else:
            update_model_obj(Veriff, {'customer_id':customer_id}, {'first_name':first_name,'last_name':last_name, 'id_type':id_type, 'id_number':id_number,'id_country':id_country, 'ip':ip, 'session_id':session_id, 'reason':reason, 'doc_valid_from':doc_valid_from, 'doc_valid_until':doc_valid_until, 'state':state, 'dob':dob, 'gender':gender, 'updated_at':get_current_datetime()})
        if str(status).lower() == "approved":
            update_model_obj(Veriff, {'customer_id':customer_id}, {'status':"submitted"})
            user_data = User.objects.filter(customer_id=customer_id, is_superuser=False).values()[0]
            send_veriff_email(user_data)
        return success_response(message="success", data=None)
   
################################ Fraud.Net Webhook ################################  
""" Fraudnet Transaction Webhook """
class FN_webhook_View(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        token = request.GET.get('token')
        body_data = request.body
        body_data_json = json.loads(body_data)
        CreateTextFile('fraudnet_webhook.txt', body_data_json)
        success_logs(body_data_json)
        transaction_id = body_data_json['order_id']
        tm_status = body_data_json['status']
        if Transaction_details.objects.filter(transaction_id=transaction_id).exists():
            Transaction_details.objects.filter(transaction_id=transaction_id).update(tm_status=str(tm_status).lower())
        return success_response(message="success", data=None)
    
################################ Subscribe Newsletter ################################  
""" Subscribe for newsletter via email """
class Subscribe_newsletter_View(APIView):

    def post(self, request, format=None):
        try:
            email = request.data.get('email')
            if not email or str(email).strip() == '':
                return bad_response("Please enter email")
            url = str(BREVO_URL)+"/contacts"
            print(url, "----------------------")
            payload = json.dumps({ "email": str(email).lower(), "listIds": [ int(LIST_ID) ]})
            headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'api-key': settings.BREVO_API_KEY,
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            response = response.json()
            if "code" in response:
                response2 = add_existing_brevo_contact(email)
                if "code" in response2:
                    return bad_response("You have already subscribed it.")            
            return success_response("Thank You for subscribing.")                          
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
                        if get_current_date() > start_date.date() or get_current_date() == start_date.date():
                            if get_current_date() < end_date.date() or get_current_date() == end_date.date():
                                if int(amount) > int(settings.REFERRAL_AMOUNT):
                                    array.append(i)
            return success_response(message="success",data=array)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
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
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

################################ Card Views (Not Using) ################################  
""" Get Last Transaction of User """
class last_transaction_view(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            data = Transaction_details.objects.filter(payment_status=transaction['pending_review'], customer_id=request.user.customer_id).values()[:1]
            return success_response("success", data)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

""" creating transaction receipt pdf """
def generate_pdf_receipt(id):
    try:
        context = {}
        if Transaction_details.objects.filter(id=id).exists():
            data = Transaction_details.objects.filter(id=id).values('transaction_id','recipient_name','send_currency', 'receive_currency','amount', 'receive_amount','date', 'reason', 'exchange_rate', 'recipient','customer_id','discount_amount','total_amount', 'updated_at')
            data = data[0]
            date = str(data['date']).replace("-","/")
            data['discount_amount'] = comma_value(data['discount_amount'])
            data['total_amount'] = comma_value(data['total_amount'])
            data['amount'] = comma_value(data['amount'])
            data['receive_amount'] = comma_value(data['receive_amount'])
            data['exchange_rate'] = comma_value(data['exchange_rate'])
            context = {'data': data}
            context.update(date=date)
            if User.objects.filter(customer_id=data['customer_id'], is_superuser=False).exists():
                customer_name = User.objects.filter(customer_id=data['customer_id'], is_superuser=False).values('First_name','Last_name','id')
                user_id = customer_name[0]['id']
                customer_name = str(str(customer_name[0]['First_name'])+" "+str(customer_name[0]['Last_name']))
                context.update(customer_name = customer_name)
                if User_address.objects.filter(user_id=int(user_id)).exists():
                    a = User_address.objects.filter(user_id=int(user_id)).values('building','street','city','state','country')
                    customer_address = str(str(a[0]['building'])+" "+str(a[0]['street'])+" "+str(a[0]['city'])+" "+str(a[0]['state'])+" "+str(a[0]['country']))
                    context.update(customer_address = customer_address)
            if data['recipient'] != None and str(data['recipient']).strip() != '':
                if Recipient.objects.filter(id=data['recipient']).exists():
                    r = Recipient.objects.filter(id=data['recipient']).values('mobile','building','street','city','state','country')
                    recipient_address = str(str(r[0]['building'])+" "+str(r[0]['street'])+" "+str(r[0]['city'])+" "+str(r[0]['state'])+" "+str(r[0]['country']))
                    recipient_mobile = r[0]['mobile']
                    context.update(recipient_mobile=recipient_mobile,recipient_address = recipient_address)
                if Recipient_bank_details.objects.filter(recipient_id=data['recipient']).exists():
                    b = Recipient_bank_details.objects.filter(recipient_id=data['recipient']).values('account_number','account_name','bank_name')
                    account_number = b[0]['account_number']
                    context.update(account_number=account_number)

        # Render the HTML template with context
        template = get_template('receipt.html')
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
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
        CreateErrorFile(file_content)
        error_logs(file_content)
        return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

def zai_users(request,offset):
    url = settings.ZAI_URL+"/users?limit=200&offset="+str(offset)
    headers = {'Authorization': 'Bearer '+zai_token(request)}
    response = requests.request("GET", url, headers=headers)
    response = response.json()
    return response



#withdraw funds from zai
def withdraw_RA_zai_funds(zai_user_id, amount, request):
    try:
        access_token = zai_token(request)
        wallet_response = zai_get_user_wallet(access_token=access_token, zai_user_id=str(zai_user_id))
        if 'errors' in wallet_response:
            return bad_response(message=wallet_response['errors'])  
        wallet_account_id = wallet_response['wallet_accounts']['id']
        bank_response = get_RA_bank_details(zai_user_id, request)
        if 'errors' in bank_response:
            return bad_response(message=bank_response['errors'])  
        bank_id = bank_response['bank_accounts']['id']

        reference_id = str(zai_reference_number(request))
        if withdraw_zai_funds.objects.filter(reference_id=reference_id).exists():
            reference_id = str(zai_reference_number(request))

        withdraw_amount = int(amount) * 100
        url = settings.ZAI_URL+"/wallet_accounts/"+wallet_account_id+"/withdraw"
        payload = json.dumps({
        "account_id": bank_id,
        "amount": str(withdraw_amount),
        "reference_id": reference_id
        })
        headers = { 'Authorization': 'Bearer '+access_token, 'Content-Type': 'application/json'}
        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        wallet_response = get_RA_zai_wallet(zai_user_id=zai_user_id, request=request)
        wallet_balance = wallet_response['wallet_accounts']['balance']
        wallet_balance = int(wallet_balance) / 100
        wallet_balance = comma_value(wallet_balance)
        #save withdra details in db with new balance
        if not 'errors' in response:
            status = "completed"
        else:
            status = "pending"
        if is_obj_exists(zai_admin_users, {'zai_user_id':zai_user_id}):
            source_data = zai_admin_users.objects.filter(zai_user_id=zai_user_id).values('bank_name')
            source_bank = source_data[0]['bank_name']
        else:
            source_bank = next((user['bank_name'] for user in ZAI_ADMIN_USERS if user['zai_user_id'] == zai_user_id), None)
        withdraw_zai_funds.objects.create(type="Payout",source_id=source_bank,destination_id="NA",status=status,reference_id=reference_id,wallet_id=wallet_account_id,amount=amount,wallet_balance=wallet_balance)
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
        CreateErrorFile(file_content)
        error_logs(file_content)
        return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))


def get_RA_bank_details(zai_user_id, request):
    url = settings.ZAI_URL+"/users/"+str(zai_user_id)+"/bank_accounts"
    headers = { 'Accept': 'application/json', 'Authorization': 'Bearer '+zai_token(request)}
    response = requests.request("GET", url, headers=headers)
    response = response.json()
    return response

def get_RA_zai_wallet(request, zai_user_id):
    url = settings.ZAI_URL+"/users/"+str(zai_user_id)+"/wallet_accounts"
    headers = { 'Accept': 'application/json', 'Authorization': 'Bearer '+zai_token(request)}
    response = requests.request("GET", url, headers=headers)
    response = response.json()
    return response



#email receipt pdf to send to customer via email
def email_transaction_receipt(transaction_id, type):
    try:
        context = {}
        user_email = None
        payment_status = None
        context2_dict = {}
        context2 = {}
        if Transaction_details.objects.filter(transaction_id=transaction_id).exists():
            data = Transaction_details.objects.filter(transaction_id=transaction_id).values('payment_status','transaction_id','recipient_name','send_currency', 'receive_currency','amount', 'receive_amount','date', 'reason', 'exchange_rate', 'recipient','customer_id','send_method','total_amount','discount_amount','updated_at')
            data = data[0]
            payment_status = str(data['payment_status'])
            date = str(data['date'])
            date = date.replace("-","/")
            comma =  comma_separated(send_amount=data['amount'], receive_amount=data['receive_amount'], exchange_rate=data['exchange_rate'] )
            comma2 =  comma_separated(send_amount=data['discount_amount'], receive_amount=data['total_amount'], exchange_rate=None )
            data['amount'] = comma['send_amount']
            data['receive_amount'] = comma['receive_amount']
            data['exchange_rate'] = comma['exchange_rate']
            data['discount_amount'] = str(comma2['send_amount']).lower()
            data['total_amount'] = comma2['receive_amount']
            context = {'data': data}
            context.update(date=date)
            context2_dict = {"discount_amount": str(data['discount_amount']),"total_amount":data['total_amount'],"send_method":data['send_method'],"transaction_id":transaction_id,"send_currency":str(data['send_currency']).upper(), "payment_status":data['payment_status'], "amount":str(data['amount']), "exchange_rate": comma['exchange_rate'], "receive_amount":data['receive_amount'], "receive_currency":data['receive_currency']}
            context2_dict.update(message="Here are the Transaction Details for Transaction ID: "+str(transaction_id))
            context2.update(date=date)
            if User.objects.filter(customer_id=data['customer_id'], is_superuser=False).exists():
                customer_name = User.objects.filter(customer_id=data['customer_id'], is_superuser=False).values('email','customer_id','First_name','Last_name','id')
                user_id = customer_name[0]['id']
                user_email = customer_name[0]['email']
                customer_id = customer_name[0]['customer_id']
                customer_name = str(str(customer_name[0]['First_name'])+" "+str(customer_name[0]['Last_name']))
                context.update(login=settings.LOGIN_LINK, support=settings.SUPPORT_CENTER_LINK,customer_name = customer_name)
                context2.update(widophremit=settings.WIDOPH_REMIT_LINK,login=settings.LOGIN_LINK,support=settings.SUPPORT_CENTER_LINK,email=user_email, customer_id=customer_id, type="transaction",customer_name=customer_name,transaction=context2_dict)
                if User_address.objects.filter(user_id=int(user_id)).exists():
                    a = User_address.objects.filter(user_id=int(user_id)).values('building','street','city','state','country')
                    customer_address = str(str(a[0]['building'])+" "+str(a[0]['street'])+" "+str(a[0]['city'])+" "+str(a[0]['state'])+" "+str(a[0]['country']))
                    context.update(customer_address = customer_address)
            if Recipient.objects.filter(id=data['recipient']).exists():
                r = Recipient.objects.filter(id=data['recipient']).values('first_name','last_name','mobile','building','street','city','state','country')
                recipient_address = str(str(r[0]['building'])+" "+str(r[0]['street'])+" "+str(r[0]['city'])+" "+str(r[0]['state'])+" "+str(r[0]['country']))
                recipient_mobile = r[0]['mobile']
                context2.update(recipient_name=str(r[0]['first_name'])+" "+str(r[0]['last_name']))
                context.update(recipient_mobile=recipient_mobile,recipient_address = recipient_address)
            if Recipient_bank_details.objects.filter(recipient_id=data['recipient']).exists():
                b = Recipient_bank_details.objects.filter(recipient_id=data['recipient']).values('account_number','account_name','bank_name')
                account_number = b[0]['account_number']
                context.update(account_number=account_number)
                context2.update(recipient_bank=b[0]['bank_name'])
            context2.update(data= email_template_image())
            # Render the HTML template with context
            template = get_template('receipt.html')
            html = template.render(context)

            # Generate a PDF file from the HTML content
            css = CSS(string='@page { size: A4; margin: 1cm }')
            pdf_file = HTML(string=html).write_pdf(stylesheets=[css])

            # Create an HTTP response with the PDF file as content, to prompt the user to download the file
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="receipt.pdf"'

            # Attach the PDF to the email
            pdf_attachment = MIMEApplication(pdf_file, _subtype='pdf')
            pdf_attachment.add_header('content-disposition', 'attachment', filename='receipt.pdf')
 
            msg = MIMEMultipart()
            msg['From'] = settings.EMAIL_HOST_USER
            msg['To'] = user_email

            if str(type).lower() == "payout":
                template2 = get_template('customer_payout.html')
                msg['Subject'] = 'Payout Confirmation for Transaction ID '+str(transaction_id)
            else:
                template2 = get_template('sender_notification.html')
                msg['Subject'] = 'WidophRemit Transaction Confirmation'

            # Attach the PDF to the email
            msg.attach(pdf_attachment)

            # Attach the HTML content as an alternative
            html2 = template2.render(context2)
            html_content2 = MIMEText(html2, 'html')
            msg.attach(html_content2)

            smtp_server = settings.EMAIL_HOST
            smtp_port = settings.EMAIL_PORT  
            smtp_username = settings.EMAIL_HOST_USER
            smtp_password = settings.EMAIL_HOST_PASSWORD
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Use TLS encryption
                server.login(smtp_username, smtp_password)
                server.sendmail(smtp_username, user_email, msg.as_string())
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
        CreateErrorFile(file_content)
        error_logs(file_content)
        return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))


class Payment_Receipt_View(APIView):
    renderer_classes=[UserRenderer]

    @csrf_exempt
    def get(self, request, pk, format=None):
        try:
            id = pk
            context = {}
            if Transaction_details.objects.filter(id=id).exists():
                data = Transaction_details.objects.filter(id=id).values('transaction_id','recipient_name','send_currency', 'receive_currency','amount', 'receive_amount','date', 'reason', 'exchange_rate', 'recipient','customer_id','discount_amount','total_amount', 'updated_at')
                data = data[0]
                date = str(data['date'])
                date = date.replace("-","/")
                comma =  comma_separated(send_amount=data['amount'], receive_amount=data['receive_amount'], exchange_rate=data['exchange_rate'])
                comma2 =  comma_separated(send_amount=data['discount_amount'], receive_amount=data['total_amount'], exchange_rate=None )
                data['discount_amount'] = comma2['send_amount']
                data['total_amount'] = comma2['receive_amount']
                data['amount'] = comma['send_amount']
                data['receive_amount'] = comma['receive_amount']
                data['exchange_rate'] = comma['exchange_rate']
                context = {'data': data}
                context.update(date=date)
                if User.objects.filter(customer_id=data['customer_id'], is_superuser=False).exists():
                    customer_name = User.objects.filter(customer_id=data['customer_id'], is_superuser=False).values('First_name','Last_name','id')
                    user_id = customer_name[0]['id']
                    customer_name = str(str(customer_name[0]['First_name'])+" "+str(customer_name[0]['Last_name']))
                    context.update(customer_name = customer_name)
                    if User_address.objects.filter(user_id=int(user_id)).exists():
                        a = User_address.objects.filter(user_id=int(user_id)).values('building','street','city','state','country')
                        customer_address = str(str(a[0]['building'])+" "+str(a[0]['street'])+" "+str(a[0]['city'])+" "+str(a[0]['state'])+" "+str(a[0]['country']))
                        context.update(customer_address = customer_address)
                if data['recipient'] and str(data['recipient']).strip() != '' and Recipient.objects.filter(id=data['recipient']).exists():
                    r = Recipient.objects.filter(id=data['recipient']).values('mobile','building','street','city','state','country')
                    recipient_address = str(str(r[0]['building'])+" "+str(r[0]['street'])+" "+str(r[0]['city'])+" "+str(r[0]['state'])+" "+str(r[0]['country']))
                    recipient_mobile = r[0]['mobile']
                    context.update(recipient_mobile=recipient_mobile,recipient_address = recipient_address)
                    if Recipient_bank_details.objects.filter(recipient_id=data['recipient']).exists():
                        b = Recipient_bank_details.objects.filter(recipient_id=data['recipient']).values('account_number','account_name','bank_name')
                        account_number = b[0]['account_number']
                        context.update(account_number=account_number)

            # Render the HTML template with context
            template = get_template('receipt.html')
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
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        
#for stripe API
def fraudnet_check_transaction(fingerprint, customer_id, fn, ln, address, city, state, postcode,customer_country_code, dob, mobile, email, recipient_id, recipient_country_code, recipient_address, recipient_name, account_no, exp_date, card_last4_digits, payment_id, card_type, send_currency, send_amount, receivecurrency, fraudnet_payment_status, transaction_id):
    url = settings.SANDBOX_URL
    payload = json.dumps({
        "customer": {
            "id": customer_id,
            "first_name": fn,
            "last_name": ln,
            "address1": address,
            "city": city ,
            "region": state,
            "postal_code": postcode,
            "country": customer_country_code,
            "dob": dob,
            "phone": mobile,
            "email": email
        },
        "seller": {
            "seller_id": recipient_id,
            "country": recipient_country_code,
            "address1": recipient_address,
            "name": recipient_name
        },
        "device": {
            "ip_address": str(get_ip()),
            "fingerprint_id": fingerprint
        },
        "account": {
            "account_id": account_no
        },
        "payment": {
            "bin": None,
            "exp_date": exp_date,
            "last_4": card_last4_digits,
            "payment_id": payment_id, # transaction_id in db
            "payment_status": "auth",
            "type": card_type,
            "actual_ccy":send_currency,
            "actual_amt": send_amount
        },
        "transaction": {
            "type": "sale",
            "iban": None,
            "ident_country": None,
            "ident_id": None,
            "ident_type": None,
            "order_currency": receivecurrency,
            "order_discount": None,
            "order_id": payment_id, #transaction_id in db
            "order_is_digital": True,
            "ordered_on": "now",
            "status": fraudnet_payment_status,
            "total_spent": send_amount,
            "user_id": customer_id,
            "user_locale": customer_country_code
        }
        })
    headers = {
        'Authorization': 'Basic '+settings.FRAUD_TOKEN,
        'Content-Type': 'application/json',
            }
    response = requests.request("POST", url, headers=headers, data=payload)
    response = response.json()
    CreateTextFile('fraudnet_transaction.txt', response)
    success_logs(response)
    return response

def application_check(customer_id, id_number, id_country, id_type, status):
    try:
        address1 = None
        city = None
        postcode = None
        state = None
        country = None
        if str(status).lower() != "approved":
            status = "new"
        if User.objects.filter(customer_id=customer_id, is_superuser=False).exists():
            obj = User.objects.filter(customer_id=customer_id, is_superuser=False).values('id','First_name','Last_name','email','mobile','Date_of_birth')
            if User_address.objects.filter(user_id=obj[0]['id']).exists():
                address = User_address.objects.filter(user_id=obj[0]['id'])
                address = address[0]
                address1 = str(address.flat)+" "+str(address.building)+" "+str(address.street)
                city = address.city
                postcode = address.postcode
                state = address.state
                country = address.country_code
            url = settings.FRAUDNET_APPLICATION_URL
            payload = json.dumps({
            "account": {
                "customer_id": customer_id,
                "dob": obj[0]['Date_of_birth'],
                "first_name": obj[0]['First_name'],
                "last_name": obj[0]['Last_name'],
                "email": obj[0]['email'],
                "phone_number": obj[0]['mobile'],
            },
            "address": {
                "address1": address1, 
                "city": str(city),
                "postal_code": str(postcode),
                "region": str(state),
                "country": str(country).upper()
            },       
            "identity": {
                "country": str(id_country).upper(),
                "id": str(id_number),
                "region": state,
                "type": "national_id"
            },
            "application": {
                "application_id": customer_id,
                "created_on": str(timezone.now()),
                "status": str(status).lower(),
            }
            })
            headers = {
            'Authorization': 'Basic '+settings.FRAUDNET_APPLICATION_TOKEN,
            'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            aml_response = response.json()
            CreateTextFile('fraudnet_application_ai.txt', aml_response)
            success_logs(aml_response)
            print(aml_response, "Application AI FN ===================")
            aml_pep_status = None
            if aml_response['success'] == True:
                if 'tags' in aml_response['data']:
                    for x in aml_response['data']['tags']:
                        if str(x['name']).lower() == 'complyadv':
                            if x['state'] == 'no_match':
                                aml_pep_status = False
                            elif x['state'] == "match" or x['state'] == "matched":
                                aml_pep_status = True
                User.objects.filter(customer_id=customer_id, is_superuser=False).update(aml_pep_status=aml_pep_status)
            return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
        CreateErrorFile(file_content)
        error_logs(file_content)
        return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

def update_fn_application_data(response, customer_id):
    try:
        aml_pep_status = "NA"
        label = ""
        tm_status = "No action triggered"
        aml_pep_status = "NA"
        rule = "No rule triggered"
        if response['success'] == True:
            risk_score = response['data']['risk_score']
            risk_group = response['data']['risk_group']
            if 'tags' in response['data']:
                for x in response['data']['tags']:
                    if str(x['name']).lower() == 'complyadv':
                        if x['state'] == 'no_match':
                            aml_pep_status = False
                        elif x['state'] == "match" or x['state'] == "matched":
                            aml_pep_status = True
                    if 'type' in x:
                        if x['type'] == "label":
                            label =  str(label +str(x['name'])+", ")
                            if label.endswith(", "):
                                label = label[:-2]
                    if 'action' in x:
                        if x['action'] != '' and x['action'] is not None:
                            tm_status = x['action']
                            if str(x['type']).lower() == "rule":
                                rule = str(x['name'])
        User.objects.filter(customer_id=customer_id, is_superuser=False).update(aml_pep_status=aml_pep_status)
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
        CreateErrorFile(file_content)
        error_logs(file_content)
        return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

def insert_sender_details(customer_email,sender,user_id,sender_address):
    User.objects.filter(email=customer_email, is_superuser=False).update(**sender)
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

def create_payment_id(transaction_id):
    payment_id = settings.PAYMENT_ID
    payment_id = payment_id.replace("-","")
    payment_id = str(str(payment_id)+str(transaction_id))
    return payment_id


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
        
def birthday_discount(transaction_id, transaction_data, request):
    try:
        discount = 0
        id = None
        type = None
        if referral_type.objects.filter(type=referral_dict['birthday']).exists():
            bdy_type_id = referral_type.objects.filter(type=referral_dict['birthday']).values('id', 'type')
            if referral.objects.filter(currency=transaction_data[0]['send_currency'] ,referral_type_id=bdy_type_id[0]['id'], status = "active").exists():
                if referral.objects.filter(referral_type_id=bdy_type_id[0]['id']).exists():
                    bdy_referral_id = referral.objects.filter(referral_type_id=bdy_type_id[0]['id']).values('id','currency','referred_by_amount')
                    bdy_referral_ids = [item['id'] for item in bdy_referral_id]
                #if user has not used any birthday voucher in current year
                if not referral_meta.objects.filter(user_id=request.user.id, is_used=True, referral_id__in=bdy_referral_ids, claimed_date__year=timezone.now().year).exists():
                    type = bdy_type_id[0]['type']
                    currency_bdy_referral_id = referral.objects.filter(currency=transaction_data[0]['send_currency'],referral_type_id=bdy_type_id[0]['id']).values('id','currency','referred_by_amount')
                    discount = currency_bdy_referral_id[0]['referred_by_amount']
                    if referral_meta.objects.filter(claimed_date__year=timezone.now().year, user_id=request.user.id, is_used=False, referral_id=bdy_referral_id[0]['id']).exists():
                        referral_meta.objects.filter(claimed_date__year=timezone.now().year, user_id=request.user.id, is_used=False, referral_id=bdy_referral_id[0]['id']).update(claimed_date=get_current_date(), claimed=True, discount=bdy_referral_id[0]['referred_by_amount'])
                        r_data = referral_meta.objects.filter(claimed_date__year=timezone.now().year, user_id=request.user.id, is_used=False, referral_id=bdy_referral_id[0]['id']).values('id')
                        id =r_data[0]['id']
                    else:
                        r = referral_meta.objects.create(user_id=request.user.id, is_used=False, referral_id=bdy_referral_id[0]['id'], claimed_date=get_current_date(), claimed=True, discount=bdy_referral_id[0]['referred_by_amount'])
                        id = r.id
        return {'referral_meta_id':id, 'type':type,'discount_amount':discount}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
        CreateErrorFile(file_content)
        error_logs(file_content)
        return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
    
class Stripe_one_step_payment_View(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        profile_serializer = UserProfileSerializer(request.user)
        transaction_id = request.data.get("transaction_id")
        card_token = request.data.get("card_token")

        if not transaction_id:
            return bad_response(message="Please enter transaction_id")
        Transaction_details.objects.filter(transaction_id=transaction_id).update(payment_status=transaction['pending_payment'], card_token= card_token, updated_at = get_current_datetime(), date=get_current_date())

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
                recipient = recipient[0]
                bank_data = list(Recipient_bank_details.objects.filter(recipient_id=obj.recipient).values('account_number','bank_name','account_name'))
                bank_dict = bank_data[0]
            else:
                return bad_response("Recipient does not exists")          
            
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

            if str(card_type_key).capitalize() != "Mastercard":
                card_type_key = str(card_type_key)+" Card"
            #updating charge id and payment status in transacton obj in DB
            transaction_data = Transaction_details.objects.filter(transaction_id=transaction_id).update(payment_status=transaction['pending_review'],payment_gateway_transaction_id = charge_id, card_type= str(card_type_key).capitalize(), send_method= str(card_type_key).capitalize(), card_token= card_token,  updated_at = get_current_datetime(), date=get_current_date())
        
            if User_address.objects.filter(user_id=profile_serializer.data['id']).exists():
                address = User_address.objects.filter(user_id=profile_serializer.data['id'])
                address = address[0]
            else:
                return bad_response(message="User Address not found")

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
            payment_status =  Transaction_details.objects.filter(transaction_id=transaction_id).values('total_amount','discount_amount','send_method','payment_status','id','send_currency', 'receive_currency', 'receive_amount')
            User.objects.filter(id=profile_serializer.data['id']).update(source_currency=str(payment_status[0]['send_currency']), destination_currency=str(payment_status[0]['receive_currency']))      

            notification.objects.create(source_id=payment_status[0]['id'], source_type="transaction", source_detail=str(send_amount)+" "+obj.send_currency, message=settings.NOTIFICATION_TRANSACTION_MSG)
            send_sms_to_RA(type="transaction",data={'transaction_id':transaction_id,'customer_id':profile_serializer.data['customer_id'],'send_currency':obj.send_currency.upper(), 'amount': str(obj.amount), 'payment_status':payment_status[0]['payment_status'],'exchange_rate':obj.exchange_rate})
            # email_to_RA(type="transaction", data={'total_amount':str(payment_status[0]['total_amount']),'discount':str(payment_status[0]['discount_amount']),'send_method':payment_status[0]['send_method'],'transaction_id':transaction_id,'email':profile_serializer.data['email'],'customer_name':str(profile_serializer.data['First_name'])+" "+str(profile_serializer.data['Last_name']),'customer_id':profile_serializer.data['customer_id'],'send_currency':obj.send_currency.upper(),'payment_status':payment_status[0]['payment_status'], 'amount': str(obj.amount), 'exchange_rate': obj.exchange_rate, 'receive_currency':obj.receive_currency, 'receive_amount':obj.receive_amount})
            email_to_RA("transaction", transaction_id)
            #sending transaction email receipt and sms to customer
            email_transaction_receipt(type="create_transaction", transaction_id=transaction_id)
            send_sms_to_customer(type= "customer",data={'transaction_id':transaction_id,'send_currency':obj.send_currency, 'send_amount':obj.amount}, user_mobile=profile_serializer.data['mobile'])
            return success_response(message=payment_status[0]['payment_status'], data={"id":str(obj.id), "transaction_id":str(transaction_id)})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

# for user dashboard after login
class Stripe_Payment_View(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None): 
        card_token = request.data.get('card_token')
        send_currency = request.data.get('send_currency')
        receive_currency = request.data.get('receive_currency')
        destination = request.data.get('destination')
        recipient_id = request.data.get('recipient_id')
        send_amount = request.data.get('send_amount')    
        receive_amount = request.data.get('receive_amount') 
        exchange_rate = request.data.get('exchange_rate')
        reason = request.data.get('reason')
        profile_serializer = UserProfileSerializer(request.user)

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
                    User.objects.filter(email=profile_serializer.data['email'], is_superuser=False).update(stripe_customer_id=stripe_customer_id)
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
            transaction_id = str(getattr(transaction_data, 'id'))  
            tid = str(getattr(transaction_data, 'id'))  
            payment_id = create_payment_id(transaction_id=transaction_id)
            # created_at = str(getattr(transaction_data, 'created_at'))  
            created_at = str(getattr(transaction_data, 'updated_at'))  
            notification.objects.create(source_id=tid, source_type="transaction", source_detail=str(send_amount)+" "+str(send_currency), message=settings.NOTIFICATION_TRANSACTION_MSG)
            t_obj = Transaction_details.objects.filter(id=tid)
            send_sms_to_RA(type="transaction",data={'transaction_id':payment_id,'customer_id':profile_serializer.data['customer_id'],'send_currency':send_currency, 'amount': send_amount, 'exchange_rate':exchange_rate})
            # email_to_RA(type="transaction", data={'send_method':"Stripe",'transaction_id':payment_id,'customer_name':str(profile_serializer.data['First_name'])+" "+str(profile_serializer.data['Last_name']), 'email':profile_serializer.data['email'],'customer_id':profile_serializer.data['customer_id'],'send_currency':send_currency, 'amount': t_obj[0].amount, 'exchange_rate':exchange_rate, 'receive_currency':t_obj[0].receive_currency, 'receive_amount':t_obj[0].receive_amount})
            email_to_RA(type="transaction", id = payment_id)
            #getting bank details 
            bank_data = Recipient_bank_details.objects.filter(recipient_id=recipient_id).values('account_number','bank_name','account_name')   
            bank_list = list(bank_data)
            bank_dict = bank_list[0]
            
            #GETTING SENDER ADDRES FROM USER ADDRESS TABLE
            sender_address = User_address.objects.filter(user_id=profile_serializer.data['id']).values('flat','building','street','postcode','city','state','country_code','country')
            sender_address = sender_address[0]
            recipient_country_code = str(recipient['country_code']).upper()
            fn = str(profile_serializer.data['First_name'])
            ln = str(profile_serializer.data['Last_name'])
            city = str(sender_address['city'])
            state = str(sender_address['state'])
            sender_country_code = str(sender_address['country_code']).upper()
            dob = str(profile_serializer.data['Date_of_birth'])
            mobile = str(profile_serializer.data['mobile'])
            email = str(profile_serializer.data['email'])
            postcode = str(sender_address['postcode'])
            account_no = str(bank_data[0]['account_number'])
            receivecurrency = str(receive_currency).upper()
            user_id = str(profile_serializer.data['customer_id'])
            transaction_data = Transaction_details.objects.filter(id=transaction_id).update( transaction_id=payment_id)
            address1 = sender_address['building']+" "+sender_address['street']
            address1 = str(address1)
            seller_address = str(recipient['building']+" "+recipient['street']+" "+recipient['city']+" "+recipient['state'])
            seller_name = recipient_name
            customer_id=user_id
            customer_country_code = sender_country_code
            recipient_address = seller_address
            address = str(address1)
            response = fraudnet_check_transaction(fingerprint, customer_id, fn, ln, address, city, state, postcode,customer_country_code, dob, mobile, email, recipient_id, recipient_country_code, recipient_address, recipient_name, account_no, exp_date, card_last4_digits, payment_id, card_type, send_currency, send_amount, receive_currency, fraudnet_payment_status, transaction_id)
            if 'source' in response:
                if response['source'] == "Duplicate Order":
                    transaction_id = str(date.today())+"0"+tid
                    response = fraudnet_check_transaction(fingerprint, customer_id, fn, ln, address, city, state, postcode,customer_country_code, dob, mobile, email, recipient_id, recipient_country_code, recipient_address, recipient_name, account_no, exp_date, card_last4_digits, payment_id, card_type, send_currency, send_amount, receive_currency, fraudnet_payment_status, transaction_id)
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
            return success_response(message=payment_status, data={"id":str(transaction_id), "transaction_id":str(payment_id)})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
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
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        
class stripe_card_list_view(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]    
    
    @csrf_exempt
    def post(self, request, format=None):
        try:
            user_serializer = UserProfileSerializer(request.user)
            customer_id = user_serializer.data['customer_id']
            if not stripe_card_details.objects.filter(customer_id=customer_id).exists():
                return bad_response(message='Card details not found')
            card_data = stripe_card_details.objects.filter(customer_id=customer_id)
            card_serializer = stripe_card_details_Serializer(card_data, many=True)
            for x in card_serializer.data:
                del[x['card_token']]
                del[x['card_id']]
                for k in x:
                    if x[k] is None:
                        x[k] == ""
                    x[k] = str(x[k])
            return success_response(message="success", data= card_serializer.data)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

class stripe_card_update_view(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]    
    
    @csrf_exempt
    def get_object(self, pk):
        try:
            return stripe_card_details.objects.get(pk=pk)
        except stripe_card_details.DoesNotExist:
            return bad_response(message="Card does not exist")
    
    # to get single card list
    def post(self, request, pk, format=None):
        type = request.data.get('type')
        try:
            card = self.get_object(pk)
            serializer = stripe_card_details_Serializer(card)
            new_dict = dict(serializer.data)
            del new_dict['card_token']
            del new_dict['card_id']
            for key in new_dict:
                if new_dict is None:
                    new_dict = "" 
                new_dict[key] = str(new_dict[key]) 
            return success_response(message="success", data=new_dict)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

    def patch(self, request, pk, format=None):
        user_serializer = UserProfileSerializer(request.user)
        card = self.get_object(pk)
        number = getattr(card, 'card_number')
        exp_month = getattr(card, 'expiry_month')
        exp_year = getattr(card, 'expiry_year')
        serializer = stripe_card_details_Serializer(card, data=request.data,partial=True)
        if serializer.is_valid():
            updated_fields_keys = serializer.validated_data.keys()
            updated_fields_values = serializer.validated_data.values()
            for key, val in zip(updated_fields_keys, updated_fields_values):
                if key == 'card_number':
                    number = val
                if key == 'expiry_month':
                    exp_month = val
                if key == 'expiry_year':
                    exp_year = val                  
            try:
                card_data = stripe.Token.create(
                card={
                        "number": number,
                        "exp_month": exp_month,
                        "exp_year": exp_year,
                    }, )
                pass
            except stripe.error.CardError as error:
                return bad_response(message=error.user_message) 
            serializer.save()
            for key in serializer.data:
                if serializer.data[key] is None:
                    serializer.data[key] = "" 
                serializer.data[key] = str(serializer.data[key]) 
            return success_response(message="success", data=serializer.data)
        return success_response(message="success", data = serializer.errors)

    @csrf_exempt
    def delete(self, request, pk, format=None):
        card = self.get_object(pk)
        if card.delete():
            return Response({'code':settings.SUCCESS_MESSAGE, 'message':settings.SUCCESS_MESSAGE})
        return Response({"code": settings.BAD_REQUEST, 'message':'False'})


# extra old API's
class failed_transactions(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]  
    def post(self, request, format=None):
        type = request.data.get('type')
        user = UserProfileSerializer(request.user)
        if not Transaction_details.objects.filter(customer_id=user.data['customer_id']).exists():
            raise serializers.ValidationError({"code":settings.BAD_REQUEST, 'message':"Transaction not found for this recipient", "Transactionnotfound":"Transaction not found for this recipient"})
        queryset = Transaction_details.objects.filter(customer_id= user.data['customer_id'], payment_status='Cancelled').values('recipient_name','receive_amount','receive_currency', 'reason','payment_status','tm_status','date')
        data = list(queryset.values())
        for x in data:
            for key in x:
                if x[key] is None:
                    x[key] = "" 
                x[key] = str(x[key]) 
        return success_response(message="success",data=data)
        
class Cloud_Currency_ViewSet(viewsets.ViewSet):
    @csrf_exempt 
    @action(detail=False, methods=['POST'])
    def login(self, request, *args, **kwargs):
        # Login API
        # sell_currency = str(request.data.get('sell_currency'))
        # buy_currency = str(request.data.get('buy_currency'))
        # amount = str(request.data.get('amount'))
        # reason = str(request.data.get('reason'))
        # reference = str(request.data.get('reference'))
        # payment_type = str(request.data.get('payment_type'))
        # payer_entity_type = str(request.data.get('payer_entity_type'))
        # payer_first_name = str(request.data.get('payer_first_name'))
        # payer_last_name = str(request.data.get('payer_last_name'))
        # payer_city = str(request.data.get('payer_city'))
        # payer_address = str(request.data.get('payer_address'))
        # payer_country = str(request.data.get('payer_country'))
        # payer_date_of_birth = str(request.data.get('payer_date_of_birth'))

        sell_currency = "AUD"
        buy_currency = "EUR"
        amount = "10"
        reason= "testing",
        reference= "testing reference",
        payment_type= "regular",
        payer_entity_type= "individual",
        payer_first_name= "Test",
        payer_last_name= "Testing",
        payer_city= "Test",
        payer_address= "Germany",
        payer_country= "DE",
        payer_date_of_birth= "1990-01-01"
        
        url1 = "https://devapi.currencycloud.com/v2/authenticate/api"
        m = MultipartEncoder(
        fields={'login_id': settings.LOGIN_ID, 'api_key': settings.CC_API_KEY})
        headers = {'Content-Type': m.content_type  }
        response = requests.request("POST", url1,data=m, headers= headers)
        response = response.json()
        auth_token = response['auth_token']

        # Get detailed currency rate API
        url2 = "https://devapi.currencycloud.com/v2/rates/detailed?buy_currency="+buy_currency+"&sell_currency="+sell_currency+"&fixed_side=sell&amount="+amount+"&conversion_date_preference=optimize_liquidity"
        headers = {
        'X-Auth-Token': auth_token,
        'Accept': 'application/json'
        }
        response2 = requests.request("GET", url2, headers=headers)
        response2 = response2.json()

        #make conversion API
        url3 = "https://devapi.currencycloud.com/v2/conversions/create"
        data = MultipartEncoder(
        fields={'buy_currency': buy_currency,
        'sell_currency': sell_currency,
        'fixed_side': 'sell',
        'amount': amount,
        'term_agreement': 'true'})
        headers = {
        'X-Auth-Token': auth_token,
        'Content-Type': data.content_type,
        'Accept': 'application/json'
        }
        response3 = requests.request("POST", url3, headers=headers, data=data)
        response3 = response3.json()
        conversion_id = response3['id']

        # Create Benificiary API
        url4 = "https://devapi.currencycloud.com/v2/beneficiaries/create"
        data= MultipartEncoder(fields={'name': 'test',
        'bank_account_holder_name': 'test',
        'bank_country': 'DE',
        'currency': 'EUR',
        'email': 'gurpreet@codenomad.net',
        'beneficiary_country': 'DE',
        'bic_swift': 'COBADEFF',
        'iban': 'DE123456789123456'})
        headers = {
        'X-Auth-Token': auth_token,
        'Content-Type': data.content_type,
        'Accept': 'application/json'
        }
        response4 = requests.request("POST", url4, headers=headers, data=data)
        response4 = response4.json()
        benificiary_id = response4['id']

        # Create Payment API
        url5 = "https://devapi.currencycloud.com/v2/payments/create"
        data = MultipartEncoder(fields={
        'currency': sell_currency,
        'beneficiary_id': benificiary_id,
        'amount': amount,
        'reason': reason,
        'reference': reference,
        'payment_type': payment_type,
        'conversion_id': conversion_id,
        'payer_entity_type': payer_entity_type,
        'payer_first_name': payer_first_name,
        'payer_last_name': payer_last_name,
        'payer_city': payer_city,
        'payer_address': payer_address,
        'payer_country': payer_country,
        'payer_date_of_birth': payer_date_of_birth})
        
        headers = {
        'X-Auth-Token': auth_token,
        'Content-Type': data.content_type,
        'Accept': 'application/json'
        }
        response5 = requests.request("POST", url5, headers=headers, data=data)
        response5= response5.json()
        return Response(response5)
     

class Stripe_new_View(APIView):
    renderer_classes = [UserRenderer]
    # permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        customer_data = stripe.Customer.create(name= "test",
                    email="test@gmail.com")
        stripe_customer_id = customer_data['id']

        token = stripe.Token.create(
            card={
                "number": "4242424242424242",
                "exp_month": 6,
                "exp_year": 2024,
                "cvc": "314",
            },
            )
        card_token = token['id']
    
        charge = stripe.Charge.create(
        amount=2000,
        currency="usd",
        source=card_token,
        description="My First Test Charge (created for API docs at https://www.stripe.com/docs/api)",
        )
        return Response(charge)


import time
#ZAI Integration
def zai_access_token(request):
    url = settings.ZAI_TOKEN_URL+"/tokens"
    payload = json.dumps({
    "grant_type": settings.ZAI_GRANT_TYPE,
    "client_id": settings.ZAI_CLIENT_ID,
    "client_secret": settings.ZAI_CLIENT_SECRET,
    "scope": settings.ZAI_SCOPE
    })
    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    response = response.json()
    return response
   
def zai_token(request):
    token_data = access_tokens.objects.filter(service_provider="zai").values()
    if not token_data:
        access_token = zai_access_token(request)
        access_token = access_token['access_token']
        access_tokens.objects.create(access_token=access_token, service_provider="zai", expires_in=settings.ZAI_TOKEN_EXPIRES_IN)
    else:
        updated_at = token_data[0]['updated_at']
        expires_in = updated_at + settings.ZAI_TOKEN_EXPIRES_IN
        if expires_in < timezone.now():
            access_token = zai_access_token(request)
            access_token = access_token['access_token']
            access_tokens.objects.filter(id=token_data[0]['id'], service_provider="zai").update(access_token=access_token, updated_at=timezone.now() ,expires_in=settings.ZAI_TOKEN_EXPIRES_IN)
        else:
            access_token = token_data[0]['access_token']
    return access_token

def zai_payid_exists(sender_pay_id):
    return zai_payid_details.objects.filter(payid= sender_pay_id).exists()


def zai_create_item(seller_id, access_token, payment_id, amount_reason, send_amount, zai_user_id, send_currency):
    if seller_id == None:
        seller_id = settings.ZAI_REMIT_USER_ID
    if '.' in str(send_amount):
        send_amount = float(send_amount)*100
    else:       
        send_amount = int(send_amount)*100
    url = settings.ZAI_URL+"/items"
    payload = json.dumps({
    "id": payment_id,
    "name": amount_reason,
    "amount": str(send_amount),
    "payment_type": "2",
    "buyer_id": zai_user_id,
    "seller_id": seller_id,
    "currency": send_currency
    # "fee_ids": "f77ac8ff-337f-4549-ab19-82da2160885c",
    })
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Bearer '+access_token }
    item_response = requests.request("POST", url, headers=headers, data=payload)
    item_response = item_response.json()
    return item_response


def zai_reference_number(request):
    random_digits = [str(random.randint(0, 9)) for _ in range(7)]
    random_digits = ''.join(random_digits)
    return random_digits





def get_user_with_id(request, zai_user_id):
    url = settings.ZAI_URL+"/users/"+zai_user_id
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer '+zai_token(request)}
    response = requests.request("GET", url, headers=headers)
    return response.json()




      
def zai_agreement_status(agreement_id, access_token, i):
    i += 1
    url = settings.ZAI_URL_ACCOUNT+"/payto/agreements/"+agreement_id
    payload = {}
    headers = { 'Authorization': 'Bearer '+access_token  }
    response = requests.request("GET", url, headers=headers, data=payload)
    response = response.json()
    if 'errors' in response:
        return Response({"code":"400", "message":response['errors']})
    agreement_status = response['status']

    if agreement_status != "ACTIVE " :
        # ======== create agreement
        url = settings.ZAI_URL_ACCOUNT+"/payto/agreements/"+agreement_id+"/create"
        headers = { 'Authorization': 'Bearer '+access_token }
        response4 = requests.request("POST", url, headers=headers, data=payload)
        response4 = response4.json()
        # if 'errors' in response4:
        #     return Response({"code":"400", "message":response4['errors']})
    if agreement_status != "ACTIVE":
        agreement_status = zai_agreement_status(agreement_id, access_token, i)
    return agreement_status

def zai_get_user_id(email):
    zai_user_id = None
    if zai_agreement_details.objects.filter(zai_email = email).exists():
        zai_user_id = zai_payid_details.objects.filter(zai_email=email).values('zai_user_id')
        zai_user_id = zai_user_id[0]['zai_user_id']
    else:
        if zai_payid_details.objects.filter(zai_email = email).exists():
            zai_user_id = zai_payid_details.objects.filter(zai_email= email).values('zai_user_id')
            zai_user_id = zai_user_id[0]['zai_user_id']
    return zai_user_id

def zai_agreement_start_date(request):
    australia_timezone = pytz.timezone('Australia/Victoria')
    current_time = datetime.now(australia_timezone)
    dt =current_time.date()
    date = str(dt.strftime('%Y-%m-%d'))
    return date






def zai_make_payment(item_id, wallet_account_id, access_token):
    url = settings.ZAI_URL+"/items/"+str(item_id)+"/make_payment"
    payload = json.dumps({ "account_id": str(wallet_account_id) })
    headers = {'Authorization': 'Bearer '+access_token, 'Content-Type': 'application/json' }
    response = requests.request("PATCH", url, headers=headers, data=payload)
    response = response.json()
    return response


def zai_get_item(payment_id, access_token):
    status = None
    url = settings.ZAI_URL+"/items/"+str(payment_id)
    headers = {'Authorization': 'Bearer '+access_token }
    response = requests.request("GET", url, headers=headers)
    response = response.json()
    if "items" in response:
        status = response['items']['state']
    return status

def zai_update_item(send_amount, payment_id, access_token):
    if '.' in send_amount:
        send_amount = int(round(float(send_amount)))*100
    else:
        send_amount = int(send_amount)*100 
    url = settings.ZAI_URL+"/items/"+str(payment_id)
    payload = json.dumps({ "amount": str(send_amount) })
    headers = { 'Authorization': 'Bearer '+access_token, 'Content-Type': 'application/json'}
    response = requests.request("PATCH", url, headers=headers, data=payload)
    response = response.json()
    return response

def apply_discount(transaction_id, referral_meta_id):
    if referral_meta.objects.filter(id=referral_meta_id, transaction_id=transaction_id).exists():
        dis = referral_meta.objects.filter(id=referral_meta_id, transaction_id=transaction_id).values('discount')  
        final_data = discount_calculation(transaction_id=transaction_id, discount_amount=dis[0]['discount'], update=True)                 
        referral_meta.objects.filter(id=referral_meta_id, transaction_id=transaction_id).update(is_used=True, claimed=True, transaction_id=transaction_id, claimed_date=get_current_date())
        return final_data['final_amount']
    else:
        return 0

class previous_transactions_View(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            profile_serializer = UserProfileSerializer(request.user)
            amount = request.data.get('amount')
            transaction_data = Transaction_details.objects.create()   
            transaction_id = str(getattr(transaction_data, 'id'))     
            payment_id = str(create_payment_id(transaction_id=transaction_id))
            Transaction_details.objects.filter(id=transaction_id).update(transaction_id=payment_id)
            return success_response(message="success",data=3)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

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
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
        CreateErrorFile(file_content)
        error_logs(file_content)
        return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
    
def concat(value, field_name):
    return Concat(Value(str(value)), F(str(field_name)), output_field=CharField())

def add_existing_brevo_contact(email):
    url = settings.BREVO_URL+"/contacts/lists/"+settings.LIST_ID+"/contacts/add"
    payload = json.dumps({
    "emails": [ str(email).lower() ]
    })
    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'api-key': settings.BREVO_API_KEY,
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()


from auth_app.helpers import upload_media_in_db

class test_View(APIView):

    def post(self, request, format=None):
        try:
            data = None
            session_id = '77a61c18-a77c-4ce2-8a15-5c026bc25354'
        
            # upload_media_in_db('c688882', session_id)

            # session_id = 'ce860524-1e56-4a7f-8c99-753ff5acb4eb'
            # secret_key = '48d6200d-c0e8-4b6a-bb69-267414fd880e'  #live      
            # signature = hmac.new(secret_key.encode('utf-8'),session_id.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()

            # data = signature

            # print(os.getcwd())
            # url = "https://stationapi.veriff.com/v1/media/ce860524-1e56-4a7f-8c99-753ff5acb4eb"

            # payload = {}
            # headers = {
            # 'X-AUTH-CLIENT': 'a1cbd614-3d1c-4e2a-b1a4-c7f24b934b4e',
            # 'X-HMAC-SIGNATURE': '5d2e35fce11ff8ea332463cd42d3fa4f1919e4a2009d4e64379ee0f18f7e0a07'
            # }

            # response = requests.request("GET", url, headers=headers, data=payload)
            # print(response)
            # if response.status_code == 200:
            #     video_path = os.getcwd()  # Replace with your desired file name and path
            #     video_content = ContentFile(b"".join(chunk for chunk in response.iter_content(chunk_size=1024)))
            #     # Create a Video instance and save the video file
            #     video = Video(title='Downloaded Video')
            #     video.file.save(video_filename, video_content)
            #     video.save()

            return success_response(message=transaction['pending_review'], data=data)   
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/views"
            CreateErrorFile(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
