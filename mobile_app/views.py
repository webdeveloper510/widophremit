from django.shortcuts import render
from Widoph_Remit.package import *
from mobile_app.sendsms import *
from auth_app.sendsms import *
from auth_app.models import *
from django.db.models import Count
from mobile_app.renderer import UserRenderers
from rest_framework.permissions import IsAuthenticated

from mobile_app.serializers import UserSerializer,User_address_List_Serializer,User_List_Serializers,User_Address_Serializer,User_update_profile_Serializer,User_Profile_Serializer,UserChangePasswordSerializer
from auth_app.views import email_to_RA
from datetime import timedelta
import datetime
from auth_app.model_queries import *
from auth_app.sendsms import *
from auth_app.emails import *
from auth_app.serializers import *

transaction = settings.TRANSACTION

# Create your views here.



def customer_id(country_code, id):
    try:
        random_digits = [str(random.randint(0, 9)) for _ in range(7)]
        random_digits = ''.join(random_digits)
        random_digits = int(random_digits[:-len(str(id))])
        customer_id = str(country_code)+str(random_digits)+str(id)
        if User.objects.filter(customer_id=customer_id).exists():
            customer_id =  customer_id(country_code, id)
        return customer_id
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        # 'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def referred_by_send_email(email, user_email):
    if settings.SEND_EMAIL == True :

        image_dict = email_template_image()
        html_content = render_to_string('referral-signup.html',{'email':email, 'data':image_dict})
        msg = EmailMultiAlternatives(
            subject='From WidophRemit',
            body='Congratulations! Your friend has signed up with your refferal code',
            from_email= settings.EMAIL_HOST_USER,
            to=[email],
                )
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.quit()

def send_otp_email(email, otp, type):
    if settings.SEND_EMAIL == True :

        image_dict = email_template_image()
        if type == "email":
            html_content = render_to_string('verifyemail.html',{'otp':otp, 'data':image_dict, 'expire_time':expire_time(type="email")})
            msg = EmailMultiAlternatives(
                subject='Email Verification Link',
                body='Email Verification Link',
                from_email= settings.EMAIL_HOST_USER,
                to=[email],
            )
        # elif type == "resend_email":
        #     html_content = render_to_string('resend_verify_email.html',{'otp':otp, 'data':image_dict, 'expire_time':expire_time(type="email")})
        #     msg = EmailMultiAlternatives(
        #         subject='Email Verification Link',
        #         body='Email Verification Link',
        #         from_email= settings.EMAIL_HOST_USER,
        #         to=[email],
        #     )
        elif type == "referred_by":
            html_content = render_to_string('referral-signup.html',{'data':image_dict})
            msg = EmailMultiAlternatives(
                subject='From WidophRemit',
                body='Congratulations! Your friend has signed up with your refferal code',
                from_email= settings.EMAIL_HOST_USER,
                to=[email],
                    )
        elif type == "reset_password":
            html_content = render_to_string('Forgotpassword.html',{'otp':otp, 'data':image_dict, 'expire_time':expire_time(type="reset_password")})
            msg = EmailMultiAlternatives(
                subject='Reset your password',
                body='Reset Password OTP',
                from_email= settings.EMAIL_HOST_USER,
                to=[email],
            )
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.quit()

def sendemail(html_content, msg):
    if settings.SEND_EMAIL == True :

        html_content = html_content
        msg = msg
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.quit()

def expire_time(type):
    if type == "email":
        delta = str(settings.EMAIL_VERIFICATION_TOKEN_EXPIRED)
    if type == "reset_password":
        delta = str(settings.RESET_PASSWORD_TOKEN_EXPIRED)
    hours = delta.split(":")[0]
    minutes = delta.split(":")[1]
    seconds = delta.split(":")[2]
    if hours != "0":     
        if hours == "1":
            expire_time = hours +" hour"
        else:
            expire_time = hours +" hours"
    if minutes != "00" or minutes != "0":
        expire_time = minutes +" minutes"
    if seconds != "00" or minutes != "0":
        expire_time = seconds +" seconds"
    return expire_time

def email_template_image():
    if settings.SEND_EMAIL == True :
    
        image_data = Email_template_images.objects.all().values('title','image')
        images = []
        image_dict = {}
        for x in image_data:
            dict = {x['title']: settings.BASE_URL+"/media/"+x['image']}
            image_dict.update(dict)
        return image_dict

def generate_active_code():
    code = int(''.join([str(random.randint(0,9)) for _ in range(6)]))
    if User.objects.filter(email_otp = code,otp=code).exists():
        code = int(''.join([str(random.randint(0,9)) for _ in range(6)]))
    if len(str(code)) != 6:
        code = str(''.join([str(random.randint(0,9)) for _ in range(1)]))
        code = code.ljust(6, code)
    return code


class Resend_signup_otp_View(APIView):
    renderer_classes=[UserRenderer]

    def post(self,request,format=None):
        mobile = request.data.get('mobile')
        if not mobile:
            return bad_response(message="Please enter mobile")    
        otp = str(generate_active_code())
        Registration_otp.objects.filter(mobile=mobile).update(otp=otp, created_at = timezone.now())
        send_sms(mobile, otp)
        return success_response(message="OTP has been resend to your mobile number", data=None)

class RegisterView(APIView):
    renderer_classes=[UserRenderers]

    def post(self,request,format=None):
        referral_code = request.data.get('referral_code')
        mobile = request.data.get('mobile')
        email = request.data.get('email')
        #checking if user mobile exists and mobile is not verified then otp will be send on mobile 
        if User.objects.filter(mobile=mobile, is_superuser=False).exists():
            return bad_response(message="Mobile number already exists!")
        if User.objects.filter(email=email, is_superuser=False).exists():
            return bad_response(message="User with this Email already exists!")
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            if referral_code is not None:
                if referral_code == "" or not User.objects.filter(referral_code=referral_code).exists():
                    return bad_response(message="Invalid referral code")
            otp = str(generate_active_code())
            if settings.HOST != "LIVE":
                # custom_mobiles = ['+61411229911','+61411223344','+610411223344','+61412022024','+610412022024','+61413022024','+610413022024','+61414022024','+610414022024','+61415022024','+610415022024','+61416022024','+610416022024','+61417022024','+610417022024']
                if mobile in CUSTOM_MOBILES:
                    cus_otp = CUSTOM_OTP
                    Registration_otp.objects.update_or_create(mobile=mobile, defaults={'otp': cus_otp, 'created_at': timezone.now()})
                    send_sms(mobile, cus_otp)
                    return Response({"code":"200","message":"OTP has been sent to your mobile number"})
                
            if Registration_otp.objects.filter(mobile=mobile).exists():
                Registration_otp.objects.filter(mobile=mobile).update(otp=otp, created_at = timezone.now())
            else:
                Registration_otp.objects.create(mobile=mobile, otp=otp)
            send_sms(mobile, otp)
            return Response({"code":"200","message":"OTP has been sent to your mobile number"})
        else:
            for v in serializer.errors.values():
                return bad_response(message=v[0])


#new registration with mobile and email otp sent
class Register_verify_View(APIView):
    renderer_classes=[UserRenderers]

    def post(self,request,format=None):
        referral_code = request.data.get('referral_code')
        mobile = request.data.get('mobile')
        email = request.data.get('email')
        promo_marketing = request.data.get('promo_marketing')
        otp = request.data.get('otp')
        fcm_token = request.data.get('fcm_token')
        apps_version = request.data.get('apps_version')
        app_update = request.data.get('app_update')
        platform = request.data.get('platform')
        if not otp:
            return bad_response(message="Please enter OTP")               
        if not Registration_otp.objects.filter(mobile=mobile,otp = otp ).exists():
            return bad_response(message="Invalid OTP")
        if not promo_marketing:
            # return Response({"code":"400","message":"You are using old version of the app please update!"})
           return Response({"code":"400","message": "You are using an old version of the app. Please update!"})

        is_verified = Registration_otp.objects.filter(mobile=mobile, otp = otp).values('created_at')          
        token_created_at = is_verified[0]['created_at']
        expire_time = token_created_at + settings.MOBILE_VERIFICATION_TOKEN_EXPIRED
        is_token_expired =  expire_time < timezone.now()
        if is_token_expired == True:
            return bad_response(message="OTP expired")
    
        #checking if user mobile exists and mobile is not verified then otp will be send on mobile 
        if User.objects.filter(mobile=mobile, is_superuser=False).exists():
            return bad_response(message="Mobile number already exists!")
        if User.objects.filter(email=email, is_superuser=False).exists():
            return bad_response(message="User with this Email already exists!")
        #saving user data into database
        
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            if referral_code is not None:
                if referral_code == "" or not User.objects.filter(referral_code=referral_code, is_superuser=False).exists():
                    return bad_response(message="Invalid referral code")
            if promo_marketing:
                if str(promo_marketing) != "0" and str(promo_marketing) != "1":
                    return bad_response("Promotional Marketing Error")
            serializer.save()
            if promo_marketing:
                User.objects.filter(mobile=mobile, is_superuser=False).update(promo_marketing=promo_marketing)
            data = User.objects.filter(email=serializer.data['email'], is_superuser=False)
            otp = str(generate_active_code())
            #creating customer id
            cust_id = customer_id(country_code=serializer.data['country_code'], id=serializer.data['id'])
            #updating OTP, cust id, and mobile in Database
            User.objects.filter(email=serializer.data['email'], is_superuser=False).update(customer_id = cust_id, mobile_verified=True, mobile=mobile, fcm_token=fcm_token,apps_version=apps_version,app_update=app_update,platform=platform)
            notification.objects.create(source_id=cust_id, source_type="user", source_detail=serializer.data['email'], message=settings.NOTIFICATION_USER_MSG)
            #sending OTP on mobile and email verification link on email
            email_activation_link = settings.EMAIL_ACTIVATION_LINK+cust_id
            send_otp_email(serializer.data['email'], otp = email_activation_link, type="email")
            #sending email to person who referred this customer
            if referral_code and User.objects.filter(referral_code=referral_code).exists():
                referred_by = User.objects.filter(referral_code=referral_code).values('email','id')
                User.objects.filter(email=serializer.data['email'], is_superuser=False).update(referred_by=referred_by[0]['id'])
            #fetching user list data to send in response
            list = User_Profile_Serializer(data, many=True)
            data = dict(list.data[0])
            
            data['digital_id_verified'] = data['is_digital_Id_verified']
            del data['is_digital_Id_verified']
            for k in data:
                data[k] = str(data[k])
                
            image_dict = email_template_image()   
            html_content = render_to_string('welcome.html', {'data':image_dict})
            msg = EmailMultiAlternatives(
                subject='Welcome to Widoph Remit',
                body='Welcome to Widoph Remit',
                from_email= settings.EMAIL_HOST_USER,
                to=[serializer.data['email']],
            )
            sendemail(html_content, msg)
            email_to_RA(type="customer", id=serializer.data['id'])
            send_sms_to_RA(type="customer", data={'email':str(serializer.data['email'])})
            user = User.objects.get(email=serializer.data['email'])
            data['token']= get_tokens_for_user(user)["access"]
            if data["transactions"] == "None":
                data["transactions"] = str(0)
            if user is not None:
                return success_response(message= "Registration successful", data=data)
            return success_response(message="Registration successful", data=data)
        else:
            for v in serializer.errors.values():
                return bad_response(message=v[0])
            
def is_obj_exists(model, filter_key):
    return model.objects.filter(**filter_key).exists()
####

class LoginView(APIView):
    renderer_classes=[UserRenderers]
    def post(self,request,format=None):
        user_email = request.data.get('email')
        mobile = request.data.get('mobile')
        password = request.data.get('password')
        apps_version = request.data.get('apps_version')
        app_update = request.data.get('app_update')
        platform = request.data.get('platform')

        email = user_email
        User.objects.filter(mobile = mobile).update(apps_version=apps_version,app_update=app_update,platform=platform)

        if not password:
            return bad_response(message="Please enter password")
        if mobile:
            if mobile == "" or mobile == None:
                return bad_response(message="Please enter mobile")
            if not User.objects.filter(mobile=mobile, is_superuser=False).exists():
                return bad_response(message = "User does not exist with this mobile number")
            if is_obj_exists(User, {'mobile':mobile, 'is_superuser':False, 'delete':True}):
                return bad_response(message="Your account access has been restricted. For assistance, please contact the administrator.")
            email = User.objects.filter(mobile=mobile).values('email','password')
            email = email[0]['email']
        if user_email:
            email = user_email
            if not User.objects.filter(email=user_email, is_superuser=False).exists():
                return bad_response(message = "User does not exist with this email address")
            if is_obj_exists(User, {'email':user_email, 'is_superuser':False, 'delete':True}):
                return bad_response("Your account access has been restricted. For assistance, please contact the administrator.")
            #checking password
            user=authenticate(email=email,password=password)
            if user is None:                   
                return bad_response(message="Password is not valid") 
            is_verified = User.objects.filter(email = email).values('is_verified','mobile_verified','mobile','customer_id')
            mobile = is_verified[0]['mobile']
            #checking is email verified or not
            if is_verified[0]['is_verified'] == False:
                email_activation_link = settings.EMAIL_ACTIVATION_LINK+is_verified[0]['customer_id']
                # send_otp_email(user_email, otp = email_activation_link, type="email")
                send_otp_email(user_email, otp = email_activation_link, type="email")
                e_mail =  User.objects.filter(email=email, is_superuser=False).values('email')
                User.objects.filter(email = e_mail[0]['email']).update(email_otp=timezone.now())
                data = User.objects.filter(email = e_mail[0]['email'])
                user_serializer = User_List_Serializers(data, many=True)
                logdict = dict(user_serializer.data[0])

                for key in logdict:
                    logdict[key] = str(logdict[key])
                return pending_verification_response(message="Please verify the link sent to your registered email.", data=logdict)            
        #validating email and password for login
        user=authenticate(email=email,password=password)
        if user is not None:
            # if settings.HOST == "LIVE":
            #     if mobile == '+61213216564':
            #         otp = '123456'
            #         User.objects.filter(mobile=mobile).update(otp = otp, updated_at = timezone.now())
            #         return Response({"code":"200","message":"OTP has been sent to your registered mobile number"})
            
            if settings.HOST != "LIVE":
                # custom_emails = ['vdsasd@gmail.com','obiyo.orji@gmail.com','obiukabiala@icloud.com','test240203@remitassure.com','test120424@remitassure.com','test130424@remitassure.com',' test140424@remitassure.com','test150424@remitassure.com']
                if user_email in CUSTOM_EMAILS:
                    email_otp = CUSTOM_OTP
                    User.objects.filter(mobile=mobile).update(otp = email_otp, updated_at = timezone.now())
                # custom_mobiles = ['+61411229911','+61411223344','+610411223344','+61412022024','+610412022024','+61413022024','+610413022024','+61414022024','+610414022024','+61415022024','+610415022024','+61416022024','+610416022024','+61417022024','+610417022024']
                if mobile in CUSTOM_MOBILES:
                    sta_otp = CUSTOM_OTP
                    User.objects.filter(mobile=mobile).update(otp = sta_otp, updated_at = timezone.now())
                else:
                    otp =  str(generate_active_code())
                    send_sms(mobile, otp)
                    User.objects.filter(mobile=mobile).update(otp = otp, updated_at = timezone.now())
                    data = User.objects.filter(email = email, is_superuser=False)
                    user_serializer = User_List_Serializers(data, many=True)
                    
            else:
                otp =  str(generate_active_code())
                send_sms(mobile, otp)
                User.objects.filter(mobile=mobile).update(otp = otp, updated_at = timezone.now())
                data = User.objects.filter(email = email, is_superuser=False)
                user_serializer = User_List_Serializers(data, many=True)
            return Response({"code":"200","message":"OTP has been sent to your registered mobile number"})
        return bad_response(message="Password is not valid")



# class ProfileView(APIView):
#     renderer_classes=[UserRenderer]
#     permission_classes=[IsAuthenticated]
#     def post(self,request,format=None):
#         try:
#             serializer = User_Profile_Serializer(request.user)
#             dict = serializer.data.copy()
#             if User_address.objects.filter(user=serializer.data['id']).exists():
#                 address = User_address.objects.filter(user_id=serializer.data['id'])
#                 address_serializer = User_address_List_Serializer(address, many=True)
#                 dict.update(address_serializer.data[0])
#             else:
#                 profile_completed = False
#             for key, value in dict.items():
#                 if not value or str(value).strip() == '':
#                     if not str(key).lower() in PROFILE_COMPLETED_OPTIONAL_LOWER_FIELDS:
#                         profile_completed = False
#                     value == ""
#             dict.update(profile_completed=profile_completed) 
#             dict['document_email'] = "ankur@codenomad.net"
#             dict['id'] = serializer.data['id']
#             for key in dict:
#                 dict[key] = str(dict[key])
#                 if key is None:
#                     key == ""
#             return success_response(message="success", data=dict)
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

""" User profile """
class ProfileView(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]

    def post(self,request,format=None):
        try:
            profile_completed = "True"
            serializer = UserProfileSerializer(request.user)
            data = dict(serializer.data)
            if is_obj_exists(User_address, {'user':serializer.data['id']}):
                address = User_address.objects.filter(user_id=serializer.data['id'])
                address_serializer = User_address_List_Serializer(address, many=True)
                data.update(address_serializer.data[0])
            else:
                profile_completed = "False"
            for key, value in data.items():
                if value is None:
                    data[key] = ""
                elif value is True:
                    data[key] = "True"
                elif value is False:
                    data[key] = "False"
                elif not value or str(value).strip() == '':
                    if not str(key).lower() in PROFILE_COMPLETED_OPTIONAL_LOWER_FIELDS:
                        profile_completed = "False"
                    data[key] = ""
                # if not value or str(value).strip() == '':
                #     if not str(key).lower() in PROFILE_COMPLETED_OPTIONAL_LOWER_FIELDS:
                #         profile_completed = "False"
                #     value == ""
            data.update(profile_completed=profile_completed)
            data.update(document_email="ankur@codenomad.net")
            
            if 'messages_list' not in data:
                data['messages_list'] = []

            complete_profile = data['profile_completed']
            if complete_profile == "True":
                data['messages_list'].append(
                    {
                        "message": "Complete your profile.",
                        "isKycCompletion": "false",
                        "isProfile": "true"
                    }
                )

            docs = data['documents']
            if docs == "pending":
                data['messages_list'].append(
                    {
                        "message": "Tier documents under review. For further details, contact ankur@codenomad.net .",
                        "isKycCompletion": "false",
                        "isProfile": "false"
                    }
                )

            if docs == "failed":
                data['messages_list'].append(
                    {
                        "message": "Tier updation failed. Kindly resubmit the documents at ankur@codenomad.net .",
                        "isKycCompletion": "false",
                        "isProfile": "false"
                    }
                )

            kyc = data['is_digital_Id_verified']          
            if kyc != "approved" and kyc != "submitted":
                print("yessss", data['is_digital_Id_verified'])
                data['messages_list'].append(
                    {
                        "message": "Verify Your Account.",
                        "isKycCompletion": "true",
                        "isProfile": "false",
                    }
                )
            if kyc == "submitted":
                print("yessss", data['is_digital_Id_verified'])
                data['messages_list'].append(
                    {
                        "message": "Your KYC has been submitted, please wait for approval .",
                        "isKycCompletion": "false",
                        "isProfile": "false",
                    }
                )
            return success_response("success", data)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))




""" Update user profile """
class UpdateProfile(APIView): 
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]
    
    def post(self, request, format=None):
        request_data = request.data
        try:
            USER_FIELDS =['First_name', 'Middle_name', 'Last_name', 'email', 'mobile', 'Date_of_birth', 'Gender', 'location', 'country_code',  'occupation', 'payment_per_annum', 'value_per_annum','flat', 'building', 'street', 'postcode', 'city', 'state', 'country' , 'country_code']
            PROFILE_COMPLETED_OPTIONAL_LOWER_FIELDS = ['middle_name','flat','stripe_customer_id','country_of_birth','is_verified','destination_currency', 'referred_by', 'gender', 'country_of_birth','aml_pep_status','address']

            user_id = request.user.id

            for key in USER_FIELDS:
                if not str(key).lower() in PROFILE_COMPLETED_OPTIONAL_LOWER_FIELDS:
                    if key in request_data and str(request_data[key]).strip() == '':
                        return bad_response("Please enter "+replace_(key))
            
            #if KYC / digital_id is not verified then user can update DOB
            if 'Date_of_birth' in request_data and str(request.user.is_digital_Id_verified).lower() != "approved":
                if request_data['Date_of_birth'] != None and str(request_data['Date_of_birth']).strip() != '':
                    update_model_obj(User, {'id':user_id}, {'Date_of_birth':request_data['Date_of_birth']})
                       
            EMAIL_MOBILE_FIELDS = ['email','mobile']
            for key in EMAIL_MOBILE_FIELDS:
                if key in request_data and is_obj_exists(User, {key: request_data[key], 'is_superuser':False}):
                    return bad_response(str(key).capitalize()+" already exists!")

            #updating user profile information via serializer
            user_data = User.objects.get(id=user_id)
            update_serializer = User_Update_Profile_Serializer(user_data, data=request.data, partial=True)
            if update_serializer.is_valid():
                update_serializer.save()
            
            #sending email verification link if user has updated his email
            if 'email' in request_data and request_data['email'] is not None and str(request_data['email']).strip() != '':
                update_model_obj(User, {'id':user_id}, {'is_verified':False})

            #middle name is optional, if user is updating profile info then update middle name otherwise update null
            if not 'Middle_name' in request_data and 'First_name' in request_data:
                update_model_obj(User, {'id':user_id}, {'Middle_name':""})
            elif 'Middle_name' in request_data and 'First_name' in request_data:
                update_model_obj(User, {'id':user_id}, {'Middle_name':request_data['Middle_name']})

            #updating tier documents
            # if 'payment_per_annum' in request_data and 'value_per_annum' in request_data:
            #     update_model_obj(User, {'id':user_id}, {'documents':'pending'})
            #     if 'Tier 1' in request_data['payment_per_annum'] and 'Tier 1' in request_data['value_per_annum']:
            #         update_model_obj(User, {'id':user_id}, {'documents':'not_required'})
            #     if 'Tier-1' in request_data['payment_per_annum'] and 'Tier-1' in request_data['value_per_annum']:
            #         update_model_obj(User, {'id':user_id}, {'documents':'not_required'})
                
            #     #updating tier values in db only during signup first time
            #     if not request.user.payment_per_annum:
            #         update_model_obj(User, {'id':user_id}, {'payment_per_annum':request_data['payment_per_annum']})
            #     if not request.user.value_per_annum:
            #         update_model_obj(User, {'id':user_id}, {'value_per_annum':request_data['value_per_annum']})

            #updating user addresss
            if not is_obj_exists(User_address, {'user_id':user_id}):
                create_model_obj(User_address, {'user_id':user_id})
            if 'location' in request_data and not 'country' in request_data:
                request_data['country'] = request_data['location']

            #if user is updating addres then update flat 
            if 'city' in request_data and not 'flat' in request_data:                
                update_model_obj(User_address, {'user_id':user_id}, {'flat':""})
            elif 'city' in request_data and 'flat' in request_data:                
                update_model_obj(User_address, {'user_id':user_id}, {'flat':request_data['flat']})

            address_data = User_address.objects.filter(user_id=user_id)
            address_serializer = User_address_Serializer(address_data[0], data=request.data, partial=True)
            if address_serializer.is_valid():
                address_serializer.save()


            #user list data
            serializer = User_list_Serializer(user_data)
            data_list = dict(serializer.data)
            data_list.update(address_serializer.data)
            return success_response("success", data_to_str([data_list])[0])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in mobile_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))



""" sending all signup emails (welcome, email erification link, referred by) """
class SendRegistrationEmails(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]
    
    def post(self,request,format=None):
        try:
            user_id = request.user.id
            if not is_obj_exists(User, {'id':user_id, 'is_superuser':False}):
                bad_response("User does not exist")            

            #creating notification and sending notifications via sms and email to WidophRemit
            notification.objects.create(source_id= request.user.customer_id, source_type="user", source_detail=request.user.email, message=settings.NOTIFICATION_USER_MSG)
            send_sms_to_RA(type="customer", data={'email':str(request.user.email)})
            email_to_RA(type="customer", id=user_id)

            #sending email verification link to user
            email_activation_link = settings.EMAIL_ACTIVATION_LINK+str(request.user.customer_id)
            send_email_verification_link(request.user.email, email_activation_link, "email")

            #sending email to person who referred this customer
            referred_by = request.user.referred_by
            user_object_referral = User.objects.filter(id=referred_by, is_superuser=False)
            referral_type_object = referral_type.objects.filter(type=referral_dict['invite'])
            #saving referral information
            if referred_by and user_object_referral.exists():
                if referral_type_object.exists():
                    referral_type_id = referral_type_object.values('id')
                    referral_data = referral.objects.filter(referral_type_id=referral_type_id[0]['id']).values()
                    if not is_obj_exists(referral_meta, {'user_id':user_id, 'referral_id':referral_data[0]['id'], 'referred_by':referred_by}):    
                        create_model_obj(referral_meta, {'user_id':user_id, 'referral_id':referral_data[0]['id'],'referred_by':referred_by, 'claimed':False, 'is_used':False, 'discount':referral_data[0]['referred_to_amount']})           
                    #saving instance for referred to    
                    if not is_obj_exists(referral_meta, {'user_id':referred_by, 'referral_id':referral_data[0]['id'], 'referred_to':user_id}):
                        create_model_obj(referral_meta, {'user_id':referred_by, 'referral_id':referral_data[0]['id'], 'referred_to':user_id, 'claimed':False, 'is_used':False, 'discount': referral_data[0]['referred_by_amount']})               
                #sending email to person who referred this customer
                referred_by_data = user_object_referral.values('email','id')
                send_referred_by_email(referred_by_data[0]['email'], request.user.email)

            #sending welcome email
            send_welcome_email(request.user.email)
            return success_response("success")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in mobile_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        
""" Old Update profile api"""
class Update_profile_view(APIView): 
    renderer_classes=[UserRenderer]
    permission_classes = [IsAuthenticated]

    @csrf_exempt
    def post(self, request, format=None):
        First_name        = request.data.get('First_name')
        Middle_name       = request.data.get('Middle_name')
        Last_name         = request.data.get('Last_name')
        email             = request.data.get('email')
        mobile            = request.data.get('mobile')
        Date_of_birth     = request.data.get('Date_of_birth')
        Gender            = request.data.get('Gender')
        flat              = request.data.get('flat')
        building          = request.data.get('building')
        street            = request.data.get('street')
        postcode          = request.data.get('postcode')
        city              = request.data.get('city')
        state             = request.data.get('state')
        location          = request.data.get('location')
        country_code      = request.data.get('country_code')
        occupation        = request.data.get('occupation')
        payment_per_annum = request.data.get('payment_per_annum')
        value_per_annum   = request.data.get('value_per_annum')
        
        request_data = request.data
        user_id     = request.user.id

        try:
            user_seriallizer = User_Profile_Serializer(request.user)
            if mobile and User.objects.filter(mobile=mobile, is_superuser=False).exists():
                return bad_response(message="Mobile number already exists!")
            if email and User.objects.filter(email=email, is_superuser=False).exists():
                return bad_response(message="Email already exists!")
            
            user_data = User.objects.get(pk=user_seriallizer.data['id'])
            serializer = User_update_profile_Serializer(user_data, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
            if not Middle_name:
                User.objects.filter(id=user_seriallizer.data['id']).update(Middle_name="")
            try:
                Date = datetime.datetime.strptime(Date_of_birth, "%Y-%b-%d").date()
                User.objects.filter(id=user_seriallizer.data['id']).update(Date_of_birth=Date)
            except ValueError:
                # If a ValueError occurs, Date_of_birth is not in the correct format
                User.objects.filter(id=user_seriallizer.data['id']).update(Date_of_birth=Date_of_birth)


            list_serializer = User_List_Serializers(user_data)
            dict = list_serializer.data.copy()
            if not User_address.objects.filter(user_id=user_seriallizer.data['id']).exists():
                User_address.objects.create(user_id=user_seriallizer.data['id'])
            if location:
                User_address.objects.filter(user_id=user_seriallizer.data['id']).update(country=location)
            if not flat:
                User_address.objects.filter(user_id=user_seriallizer.data['id']).update(flat="")
            if flat:
                User_address.objects.filter(user_id=user_seriallizer.data['id']).update(flat=flat)
            if not building:
                User_address.objects.filter(user_id=user_seriallizer.data['id']).update(building="")
            if building:
                User_address.objects.filter(user_id=user_seriallizer.data['id']).update(building=building)
            if not postcode:
                User_address.objects.filter(user_id=user_seriallizer.data['id']).update(postcode="")
            if postcode:
                User_address.objects.filter(user_id=user_seriallizer.data['id']).update(postcode=postcode)
            if not street:
                User_address.objects.filter(user_id=user_seriallizer.data['id']).update(street="")
            if street:
                User_address.objects.filter(user_id=user_seriallizer.data['id']).update(street=street)
                
            if not city:
                User_address.objects.filter(user_id=user_seriallizer.data['id']).update(city="")
            if city:
                User_address.objects.filter(user_id=user_seriallizer.data['id']).update(city=city)
            if not state:
                User_address.objects.filter(user_id=user_seriallizer.data['id']).update(state="")
            if state:
                User_address.objects.filter(user_id=user_seriallizer.data['id']).update(state=state)
            if not country_code:
                User_address.objects.filter(user_id=user_seriallizer.data['id']).update(country_code="")
            if country_code:
                User_address.objects.filter(user_id=user_seriallizer.data['id']).update(country_code=country_code)

            key = str(type).replace("_"," ").title()
            user_data = User.objects.filter(id=request.user.id).values()[0]
            #updating tier documents
            if 'payment_per_annum' in request_data and 'value_per_annum' in request_data:
                update_model_obj(User, {'id':user_id}, {'documents':'verification_pending'})
                if 'Tier 1' in request_data['payment_per_annum'] and 'Tier 1' in request_data['value_per_annum']:
                    update_model_obj(User, {'id':user_id}, {'documents':'not_required'})
                if 'Tier-1' in request_data['payment_per_annum'] and 'Tier-1' in request_data['value_per_annum']:
                    update_model_obj(User, {'id':user_id}, {'documents':'not_required'})
                
                #updating tier values in db only during signup first time
                if not request.user.payment_per_annum:
                    update_model_obj(User, {'id':user_id}, {'payment_per_annum':request_data['payment_per_annum']})
                if not request.user.value_per_annum:
                    update_model_obj(User, {'id':user_id}, {'value_per_annum':request_data['value_per_annum']})

                #send admin mail
                if 'Tier-2' in payment_per_annum or 'Tier-3' in payment_per_annum or 'Tier-2' in value_per_annum or 'Tier-3' in value_per_annum:
                    update_model_obj(User, {'id': request.user.id}, {'documents': 'verification_pending'})
                    tier_value = payment_per_annum if 'Tier-2' in payment_per_annum or 'Tier-3' in payment_per_annum else value_per_annum

                    send_update_tier_email_to_RA(user_data, {'key': key, 'value': tier_value})
                    send_update_tier_email_to_customer(user_data, {'key': key, 'value': tier_value})
                    return Response({"code":"200","message":"Please mail your documents at ankur@codenomad.net to update your account usage successfully.","document_email":"ankur@codenomad.net"})
                    

                send_update_tier_email_to_RA(user_data, {'key':key, 'value':value_per_annum})
                send_update_tier_email_to_customer(user_data, {'key':key, 'value':value_per_annum})
                # return Response({"code":"200","message":"Please mail your documents at ankur@codenomad.net to update your account usage successfully.","document_email":"ankur@codenomad.net"})
            
            address_components = [street, city, state, postcode,location]
            address_web = ','.join(filter(None, address_components))
            User_address.objects.filter(user_id=user_seriallizer.data['id']).update(address=address_web)
            # address_web = flat+','+building+','+street+','+city+','+state+','+country_code+','+location+','+postcode
            # User_address.objects.filter(user_id=user_seriallizer.data['id']).update(address=address_web)
            address_data = User_address.objects.filter(user_id=user_seriallizer.data['id'])
            address_serializer = User_Address_Serializer(address_data[0], data=request.data, partial=True)
            if address_serializer.is_valid():
                address_serializer.save()
                dict.update(address_serializer.data)
                dict['id'] = user_seriallizer.data['id']
                for k in dict:
                    dict[k] = str(dict[k])
                    if k is None:
                        dict[k] = ""
                return success_response(message="success", data = dict)
       
            return bad_response(message=str(serializer.errors))
        except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))



class VerifyMobileView(APIView):
    renderer_classes = [UserRenderers]

    def post(self, request, format=None):
        user_email = request.data.get('email')
        mobile = request.data.get('mobile')
        otp = request.data.get('otp')
        page = request.data.get('page') #page is used to send verification email registration time and page will be register
        fcm_token = request.data.get('fcm_token')
        apps_version = request.data.get('apps_version')
        app_update = request.data.get('app_update')
        platform = request.data.get('platform')


        if not otp:
            return bad_response(message="Please enter OTP")
        if mobile:
            if not User.objects.filter(mobile = mobile).exists():
                return bad_response(message="Mobile does not exist")
            if not User.objects.filter(mobile=mobile, otp = otp ).exists():
                return bad_response(message="Invalid OTP")
            is_verified = User.objects.filter(mobile=mobile, otp = otp).values('is_digital_Id_verified','mobile_verified','updated_at', 'email', 'password')
            email = is_verified[0]['email']
        
        if user_email:
            email = user_email
        else:
            if not User.objects.filter(email = email, otp = otp).exists():
                return bad_response(message="Invalid OTP")
        is_verified = User.objects.filter(email=email, otp = otp).values('is_digital_Id_verified','mobile_verified', 'is_verified','updated_at', 'email', 'password',)          
        token_created_at = is_verified[0]['updated_at']

        if mobile == '+61213216564':
            expire_time = token_created_at + datetime.timedelta(days=3)
            is_token_expired =  expire_time < timezone.now()
        else:
            expire_time = token_created_at + settings.MOBILE_VERIFICATION_TOKEN_EXPIRED
            is_token_expired =  expire_time < timezone.now()
        if is_token_expired == True:
            return bad_response(message="OTP expired")
        
        data = User.objects.filter(email = email)
        customer = User.objects.filter(email = email).values('customer_id')
        cos  = customer[0]['customer_id']
        ha =[]
        que  = Transaction_details.objects.filter(customer_id=cos).values('payment_status')
        for i in que:
            if str(i['payment_status']) != str(transaction['incomplete']):
                ha.append(i)
        count = len(ha)
        #fetching user_serializer data to send in response
        user_serializer = User_List_Serializers(data, many=True)
        data = dict(user_serializer.data[0])
        for key in data:
            data[key] = str(data[key])
        data.update(digital_id_verified = str(is_verified[0]['is_digital_Id_verified']))
        pa = data["transactions"]
        print("fsasdfsdf",pa)
        # if email:
        #     sa = User.objects.filter(email=email).values('app_update','occupation')[0]
        #     upp = sa['app_update'] 
        #     occp = sa['occupation'] 
        #     print("uuuuuuu",upp)
        #     print("sssssssss",occp)
        # if occp == 'old_user' or upp == None:
        #     return Response({"code": "400", "message": "You are using an old version of the app. Please update!"})
        if user_email:
            User.objects.filter(email=email, otp=otp).update(mobile_verified=True, fcm_token=fcm_token,apps_version=apps_version,app_update=app_update,platform=platform)
        else:
            User.objects.filter(mobile=mobile, otp=otp).update(mobile_verified=True, fcm_token=fcm_token,apps_version=apps_version,app_update=app_update,platform=platform)
        if page:
            # sending Welcome Email if user has signed up    
            image_dict = email_template_image()   
            html_content = render_to_string('welcome.html', {'data':image_dict})
            msg = EmailMultiAlternatives(
                subject='Welcome to Widoph Remit',
                body='Welcome to Widoph Remit',
                from_email= settings.EMAIL_HOST_USER,
                to=[email],
            )
            sendemail(html_content, msg)
        user = User.objects.get(email=email)
        data['token']= get_tokens_for_user(user)['access']

        return Response({"code": "200", "data": data})
        
        if data["transactions"] == "None":
            pa = "0"
        
        if email:
            sa = User.objects.filter(email=email).values('app_update','apps_version','user_check','is_digital_Id_verified')[0]
            version = sa['apps_version']
            upp = sa['app_update']
            user_check = sa['user_check']
            is_digital_Id_verified = sa['is_digital_Id_verified']
        # if upp == None:
        #     return Response({"code": "400", "message": "You are using an old version of the app. Please update!"})
        # if version == None:
        #     return Response({"code": "400", "message": "You are using an old version of the app. Please update!"})
        # if data["occupation"] == "old_user" and upp is None:
        #     return Response({"code": "400", "message": "You are using an old version of the app. Please update!"})
        
        # elif data["occupation"] == "old_user":
        #     User.objects.filter(email=email).update(occupation= "NA")
        #     data["transactions"] = pa
        #     return success_response(message= "Login successful", data=data)
            # return Response({"code": "400", "message": "You are using an old version of the app. Please update!"})
        elif is_digital_Id_verified != "approved":
            if user_check == 'spam':
                return Response({"code": "400", "message": "Your account isn't verified. Log in to WidophRemit.com for KYC."})
            else:
                data["transactions"] = pa
                if user is not None:
                    update_last_login(None, user)
                    return success_response(message= "Login successful", data=data)
        else:

            data["transactions"] = pa
            if user is not None:
                # token= get_tokens_for_user(user)
                update_last_login(None, user)
                # login_notify(request)
                return success_response(message= "Login successful", data=data)




class GetResetOtpMobileView(APIView):
    renderer_classes=[UserRenderer]
    def post(self, request, format=None):
        email = request.data.get('email')
        mobile = request.data.get('mobile')

        if mobile == '+61213216564':
            sta_otp = '123456'
            User.objects.filter(mobile=mobile).update(otp=sta_otp, updated_at=timezone.now())
            user = User.objects.filter(mobile = mobile).values('customer_id')
            customer_id = user[0]['customer_id']
            return success_response(message = 'OTP has been sent to your mobile.', data={'customer_id':customer_id})
        else:
            if mobile:
                if not User.objects.filter(mobile=mobile).exists():
                    return bad_response(message="You are not a registered user")
                if is_obj_exists(User, {'mobile':mobile, 'is_superuser':False, 'delete':True}):
                    return bad_response("Your account access has been restricted. For assistance, please contact the administrator.")
                user = User.objects.filter(mobile = mobile).values('customer_id')
                customer_id = user[0]['customer_id']
                otp = str(generate_active_code())
                send_sms(mobile, otp)
                User.objects.filter(mobile=mobile).update(otp=otp, updated_at=timezone.now())
                return success_response(message = 'OTP has been sent to your mobile.', data={'customer_id':customer_id})
            if email:
                if not email:
                    return bad_response(message="Please enter email")
                if email and not User.objects.filter(email=email).exists():
                    return bad_response(message="You are not a registered user")
                if is_obj_exists(User, {'email':email, 'is_superuser':False, 'delete':True}):
                    return bad_response("Your account access has been restricted. For assistance, please contact the administrator.")
                user = User.objects.filter(email = email).values('customer_id')
                customer_id = user[0]['customer_id']
                otp = str(generate_active_code())
                User.objects.filter(customer_id=customer_id).update(otp=otp, updated_at=timezone.now())
                image_dict = email_template_image()  
                html_content = render_to_string('Forgotpassword.html',{'otp':otp, 'data':image_dict, 'expire_time':expire_time(type="reset_password")})
                msg = EmailMultiAlternatives(
                    subject='Reset your password',
                    body='Reset Password OTP',
                    from_email= settings.EMAIL_HOST_USER,
                    to=[email],
                )
                sendemail(html_content, msg)
                return success_response(message = 'OTP has been sent to your email.', data={'customer_id':customer_id})
    

class ResetConfirmOtpView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        customer_id = request.data.get('customer_id')
        reset_password_code = request.data.get('reset_password_otp')
        if not customer_id:
            return bad_response(message= "Please enter customer_id")
        if not reset_password_code:
            return bad_response(message="Please enter OTP") 
       
        if not User.objects.filter(customer_id=customer_id, is_superuser=False).exists():
            return bad_response(message= "Inavlid customer_id")
        
        if not User.objects.filter(customer_id=customer_id, otp=reset_password_code, is_superuser=False).exists():
            return bad_response(message="Invalid OTP")
        created_time = User.objects.filter(customer_id=customer_id, otp=reset_password_code, is_superuser=False).values('updated_at')
        created_time = created_time[0]['updated_at']
        expire_time =  created_time + settings.RESET_PASSWORD_TOKEN_EXPIRED
        is_token_expired =  expire_time < timezone.now()
        if is_token_expired == True:
            return bad_response(message="OTP expired") 
        User.objects.filter(customer_id=customer_id).update(otp=None)
        return Response({"code":"200","message":"OTP is confirmed"})
            

class ForgotPassword(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        customer_id = request.data.get('customer_id')
        password = request.data.get('password')
        if not customer_id:
            return bad_response(message= "Please enter customer_id")
        if not password:
            return bad_response(message="Please enter password")
        da = User.objects.filter(customer_id=customer_id).values('delete')[0]
        cus = da['delete']
        if cus == True:
            return bad_response("Your account access has been restricted. For assistance, please contact the administrator.")
        if not User.objects.filter(customer_id=customer_id, is_superuser=False).exists():
            return bad_response(message= "Inavlid customer_id")

        user = User.objects.get(customer_id=customer_id)
        user.set_password(password)
        user.save()
        data2 = User.objects.filter(customer_id=customer_id, is_superuser=False)
        list = User_Profile_Serializer(data2, many=True)
        data2 = dict(list.data[0])
        data2['digital_id_verified'] = data2['is_digital_Id_verified']
        del data2['is_digital_Id_verified']
        for k in data2:
            data2[k] = str(data2[k])
        User.objects.filter(customer_id=customer_id, is_superuser=False).update(otp=None)
        return success_response(message='Password Reset Successfully', data=data2)

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = UserChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def post(self, request, *args, **kwargs):
        user_serializer = User_Profile_Serializer(request.user)
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not old_password:
            return bad_response(message='Please enter old password')
        if not new_password:
            return bad_response(message="Please enter new password")
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return bad_response(message="Wrong old password")
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            email = User_Profile_Serializer(request.user)
            return success_response(message='Password updated successfully', data= None)   
        return bad_response (message= serializer.errors)
    
    
class Resend_OTP_View(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        email = request.data.get('email')
        mobile = request.data.get('mobile')
        new_mobile = request.data.get('new_mobile')
        if mobile == '+61213216564':
            sta_otp = '123456'
            User.objects.filter(mobile=mobile).update(otp=sta_otp, updated_at=timezone.now())
            return success_response(message= "OTP has been sent to your registered mobile number.", data=None)
        # type = request.data.get('type')
        else:
            if not email and not mobile:
                return bad_response(message="Please enter email or mobile")   
            if mobile:
                if not User.objects.filter(mobile = mobile, is_superuser=False).exists():
                    return bad_response(message="Mobile does not exist") 
                if is_obj_exists(User, {'mobile':mobile, 'is_superuser':False, 'delete':True}):
                    return bad_response("Your account access has been restricted. For assistance, please contact the administrator.")
                otp = str(generate_active_code())
                if new_mobile:
                    send_sms(new_mobile,otp)
                else:
                    otp_test = send_sms(mobile,otp)
                User.objects.filter(mobile=mobile).update(otp=otp, updated_at=timezone.now())
                return success_response(message= "OTP has been sent to your registered mobile number.", data=None)
            else:
                if not User.objects.filter(email = email).exists():
                    return bad_response(message="Email does not exist")  
                if is_obj_exists(User, {'email':email, 'is_superuser':False, 'delete':True}):
                    return bad_response("Your account access has been restricted. For assistance, please contact the administrator.")
                image_dict = email_template_image()  
                customer_id = User.objects.filter(email=email).values('customer_id','mobile')
                mobile = customer_id[0]['mobile']
                customer_id = customer_id[0]['customer_id']
                # time = timezone.now()
                otp = str(generate_active_code())
                send_sms(mobile,otp)
                User.objects.filter(mobile=mobile, is_superuser=False).update(otp=otp, updated_at=timezone.now())
                if type == "email":
                    #sending email verification link
                    email_activation_link = settings.EMAIL_ACTIVATION_LINK+customer_id
                    send_otp_email(email, otp = email_activation_link, type="email")
                    return success_response(message= "Email verification link has been sent to your email address. Please check your email.", data=None)
                return success_response(message= "OTP has been sent to your registered mobile number.", data=None)


class TestOtp(APIView):
    renderer_classes = [UserRenderer]

    def get(self, request, format=None):
        mobile = request.data.get('mobile')
        if mobile:
            if Registration_otp.objects.filter(mobile=mobile).exists():
                reg = Registration_otp.objects.filter(mobile=mobile).values('otp')
                reg_otp =reg[0]['otp']
            else:
                reg_otp = "Mobile number does not exists."
            if User.objects.filter(mobile=mobile).exists():
                user = User.objects.filter(mobile = mobile).values('otp')
                us = user[0]['otp']
            else:
                us = "Mobile number does not exists."  
            return success_response(message = 'Get otp', data={'reg_otp':reg_otp, 'user_otp':us})
        return bad_response("Please enter mobile number.")
        

""" To check user is activated or disabled """
class Is_User_Exists(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]
    
    def get(self,request,format=None):
        try:
            if is_obj_exists(User, {'id':request.user.id}):
                is_deleted_value = "True" if request.user.delete is True else "False"
                return success_response("success", data={'is_deleted':is_deleted_value})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        

""" Create referral link to invite user """
class ReferralLink(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            referral_code = request.user.referral_code
            referral_link = settings.BASE_URL+"/"+referral_code
            return success_response("success", {'link':referral_link, 'referral_code':referral_code})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))



############################ Update Tiers Request ################################
""" Send Tier Value To Customer and WidophRemit """
class Update_tier_request_view(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        value = request.data.get('value')
        type = request.data.get('type')
        try:
            if not value and not value:
                return bad_response("Please enter value")   
            if not type and not type:
                return bad_response("Please enter type")   
            key = str(type).replace("_"," ").title()
            user_data = User.objects.filter(id=request.user.id).values()[0]


            if 'Tier-2' in value or 'Tier-3' in value:
                update_model_obj(User, {'id':request.user.id}, {'documents':'verification_pending'})

                send_update_tier_email_to_RA(user_data, {'key':key, 'value':value})
                send_update_tier_email_to_customer(user_data, {'key':key, 'value':value})
                return Response({"code":"200","message":"Please mail your documents at ankur@codenomad.net to update your account usage successfully.","document_email":"ankur@codenomad.net"})
            #update
            if 'Tier 1' in value or 'Tier-1' in value:
                update_model_obj(User, {'id':request.user.id}, {'documents':'not_required'})
            else:
                update_model_obj(User, {'id':request.user.id}, {'documents':'verification_pending'})
                
            send_update_tier_email_to_RA(user_data, {'key':key, 'value':value})
            send_update_tier_email_to_customer(user_data, {'key':key, 'value':value})
            return success_response("success")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
   


""" verify otp and creating user in DB """
class RegistrationVerify(APIView):
    renderer_classes=[UserRenderer]

    def post(self,request,format=None):
        referral_code = request.data.get('referral_code')
        promo_marketing = request.data.get('promo_marketing')
        mobile = request.data.get('mobile')
        otp = request.data.get('otp')
        fcm_token = request.data.get('fcm_token')
        apps_version = request.data.get('apps_version')
        app_update = request.data.get('app_update')
        platform = request.data.get('platform')

        registration_otp_object = Registration_otp.objects.filter(mobile=mobile, otp=otp)
        user_object = User.objects.filter(mobile=mobile, is_superuser=False)
        user_object_referral_code = User.objects.filter(referral_code=referral_code, is_superuser=False)
     
        if not otp:
            return bad_response("Please enter OTP")    
        try:
            custom_otp = False
            if settings.HOST != "LIVE":
                if str(mobile) in settings.CUSTOM_MOBILES:
                    custom_otp = True
                    if str(otp) != str(settings.CUSTOM_OTP):
                        return bad_response("Invalid OTP")
            if custom_otp == False:
                if not registration_otp_object.exists():
                    return bad_response("Invalid OTP")   
                is_verified = registration_otp_object.values('created_at')          
                token_created_at = is_verified[0]['created_at']
                expire_time = token_created_at + settings.MOBILE_VERIFICATION_TOKEN_EXPIRED
                is_token_expired =  expire_time < timezone.now()
                if is_token_expired == True:
                    return bad_response("OTP expired")          
            
            #checking if user mobile exists and mobile is not verified then otp will be send on mobile 
            if user_object.exists():
                return bad_response("Mobile number already exists!")
            
            #saving user data into database
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                if referral_code is not None:
                    if str(referral_code).strip() == "" or not user_object_referral_code.exists():
                        return bad_response("Invalid referral code")
                if promo_marketing:
                    if str(promo_marketing) != "0" and str(promo_marketing) != "1":
                        return bad_response("Promotional Marketing Error")  
                serializer.save()
                if promo_marketing:
                    user_object.update(promo_marketing=promo_marketing)
                data = User.objects.filter(id=serializer.data['id'])
                otp = str(generate_activation_code())
               
                cust_data = create_customer_id_and_referral_code(email=serializer.data['email'] ,country_code=serializer.data['country_code'], id=serializer.data['id'])
                #updating OTP, cust id, and mobile in Database
                User.objects.filter(email=serializer.data['email'], is_superuser=False).update(referral_code=cust_data['referral_code'], customer_id = cust_data['customer_id'], mobile_verified=True, mobile=mobile, fcm_token=fcm_token,apps_version=apps_version,app_update=app_update,platform=platform)
               
                #saving referred by person id in DB
                if referral_code and User.objects.filter(referral_code=referral_code, is_superuser=False).exists():
                    referred_by = User.objects.filter(referral_code=referral_code, is_superuser=False).values('email','id')
                    User.objects.filter(email=serializer.data['email'], is_superuser=False).update(referred_by=referred_by[0]['id'])
                #fetching user list data to send in response
                list = User_Profile_Serializer(data, many=True)
                data = dict(list.data[0])
                data['digital_id_verified'] = data['is_digital_Id_verified']
                del data['is_digital_Id_verified']

                data = {k: str(v) if v is not None else "" for k, v in data.items()}
                
                user = User.objects.get(id=serializer.data['id'])
                data['token']= get_tokens_for_user(user)["access"]
                if data["transactions"] == "None":
                    data["transactions"] = str(0)
                if user is not None:
                    return success_response(message= "Registration successful", data=data)
                return success_response(message="Registration successful", data=data)
            else:
                for v in serializer.errors.values():
                    return bad_response(v[0])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in mobile_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
