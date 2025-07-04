from Widoph_Remit.package import *
from auth_app.sendsms import *
import datetime
import math
from Widoph_Remit.response import *
from dateutil import parser
from .serializers import *
from .model_queries import *
from .helpers import *
from .emails import *
from Widoph_Remit.helpers import *
from payment_app.helper import CreateErrorFile, CreateTextFile

referral_dict = settings.REFERRALS

############################ Registration Process Views ############################
""" Signup validation and sending signup OTP on mobile """
class RegistrationCheck(APIView):
    renderer_classes=[UserRenderer]

    def post(self,request,format=None):
        try:
            data = request.data
            keys = ['mobile','email','password','location','mobile','country_code']

            for k in keys:
                if not k in data or str(data[k]).strip() == '':
                    return bad_response("Please enter "+ replace_(k))
            if is_obj_exists(User, {'mobile':data['mobile'], 'is_superuser':False}):
                return bad_response("Mobile number already exists!")
            if is_obj_exists(User, {'email':data['email'], 'is_superuser':False}):
                return bad_response("User with this email already exists!")            
            if 'referral_code' in data and not is_obj_exists(User, {'referral_code':data['referral_code'], 'is_superuser':False}):
                return bad_response("Invalid referral code")
            if 'promo_marketing' in data and str(data['promo_marketing']) != "0" and str(data['promo_marketing']) != "1":
                return bad_response("Promotional Marketing Error")  
            response = update_registration_otp(data['mobile'], str(generate_activation_code()))
            if response['code'] == 400:
                return bad_response(response['message'])
            return success_response("OTP has been sent to your mobile number")
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
            serializer = UserRegistrationSerializer(data=request.data)
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
                User.objects.filter(email=serializer.data['email'], is_superuser=False).update(referral_code=cust_data['referral_code'], customer_id = cust_data['customer_id'], mobile_verified=True, mobile=mobile, user_type="web")
               
                #saving referred by person id in DB
                if referral_code and User.objects.filter(referral_code=referral_code, is_superuser=False).exists():
                    referred_by = User.objects.filter(referral_code=referral_code, is_superuser=False).values('email','id')
                    User.objects.filter(email=serializer.data['email'], is_superuser=False).update(referred_by=referred_by[0]['id'])
                #fetching user list data to send in response
                list = UserProfileSerializer(data, many=True)
                data = dict(list.data[0])
                data['digital_id_verified'] = data['is_digital_Id_verified']
                del data['is_digital_Id_verified']
                for k in data:
                    data[k] = str(data[k])
                
                user = User.objects.get(id=serializer.data['id'])
                if user is not None:
                    token= get_tokens_for_user(user)  
                    return token_response(token=token['access'], message= "Registration successfull", data=data)
                return success_response(message="Registration successfull", data=data)
            else:
                for v in serializer.errors.values():
                    return bad_response(v[0])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
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

            #creating notification and sending notifications via sms and email to RemitAssure
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
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

""" resend signup otp """
class ResendSignupOtp(APIView):
    renderer_classes=[UserRenderer]

    def post(self,request,format=None):
        mobile = request.data.get('mobile')
        try:
            if not mobile or str(mobile).strip() == '':
                return bad_response("Please enter mobile")    
            otp = str(generate_activation_code())
            if is_obj_exists(Registration_otp, {'mobile':mobile}):
                update_model_obj(Registration_otp, {'mobile':mobile}, {'otp':otp, 'created_at':get_current_datetime()})
            else:
                create_model_obj(Registration_otp, {'mobile':mobile, 'otp':otp})
            send_sms(mobile, otp)
            return success_response("OTP has been resend to your mobile number")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

############################ Login Process Views ###################################
""" Verify OTP to login """
class Verify_OTP(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        email = request.data.get('email')
        mobile = request.data.get('mobile')
        otp = request.data.get('otp')
        try:
            custom_otp = False
            if not email and not mobile:
                return bad_response("Please enter email or mobile")
            if not otp or str(otp).strip() == '':
                return bad_response("Please enter OTP")
            if mobile:
                if not is_obj_exists(User, {'mobile':mobile, 'is_superuser':False, 'delete':False}):
                    return bad_response("User does not exists!")
                # user_data = filter_model_objs(User, {'mobile':mobile, 'is_superuser':False, 'delete':False}, {'is_digital_Id_verified','mobile_verified','updated_at', 'email', 'password'})
                user_data = get_all_filter_values(User, {'mobile':mobile, 'is_superuser':False, 'delete':False})
                email = user_data[0]['email']
            else:
                if not is_obj_exists(User, {'email':email, 'is_superuser':False, 'delete':False}):
                    return bad_response("User does not exists!")
                user_data = get_all_filter_values(User, {'email':email, 'is_superuser':False, 'delete':False})
            
            #checking custom otp for custom users
            if settings.HOST != "LIVE":
                    if str(email).lower() in CUSTOM_EMAILS or str(mobile) in CUSTOM_MOBILES:
                        custom_otp = True
                        if str(otp) != str(CUSTOM_OTP):
                            return bad_response("Invalid OTP")    
 
            #checking otp                         
            if custom_otp == False:
                if not is_obj_exists(User, {'email':email, 'otp':otp, 'is_superuser':False}):
                    return bad_response("Invalid OTP")
                if is_mobile_token_expired(user_data[0]['updated_at']):
                    return bad_response(message="OTP expired")
            
            #get user list and access token
            user = User.objects.filter(email=email, is_superuser=False)
            serializer = User_list_Serializer(user, many=True)
            dict(serializer.data[0]).update(digital_id_verified = str(user_data[0]['is_digital_Id_verified']).lower())
            update_model_obj(User, {'email':email, 'otp':otp, 'is_superuser':False}, {'mobile_verified':True, 'otp':None})
            user = User.objects.get(email=email, delete=False, is_superuser=False)            
            if user is not None:
                token = get_tokens_for_user(user)
                update_last_login(None, user)
                return token_response("Login successfull", token['access'], data_to_str(serializer.data)[0])
            return bad_response("Password is not valid!")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

""" Login validation to check password and send otp on mobile """
class Login(APIView):
    renderer_classes=[UserRenderer]

    def post(self,request,format=None):
        user_email = request.data.get('email')
        mobile = request.data.get('mobile')
        password = request.data.get('password')
        email = user_email
        try:
            if not mobile and not email:
                return bad_response(message="Please enter email or mobile")
            if not password:
                return bad_response(message="Please enter password")
            
            #if user will login with mobile 
            if mobile:
                if not is_obj_exists(User, {'mobile':mobile, 'is_superuser':False}):
                    return bad_response("User does not exists!")
                if is_obj_exists(User, {'mobile':mobile, 'is_superuser':False, 'delete':True}):
                    return bad_response("Your account access has been restricted. For assistance, please contact the administrator.")
                user_data = get_all_filter_values(User, {'mobile':mobile, 'is_superuser':False})
                email = user_data[0]['email']
            
            #if user will login with an email 
            if user_email:
                if not is_obj_exists(User, {'email':email, 'is_superuser':False}):
                    return bad_response("User does not exists!")
                if is_obj_exists(User, {'email':user_email, 'is_superuser':False, 'delete':True}):
                    return bad_response("Your account access has been restricted. For assistance, please contact the administrator.")
                user = authenticate(email=email, password=password)
                if user is None:                   
                    return bad_response("Password is not valid")              
                user_data = get_all_filter_values(User, {'email':email, 'is_superuser':False})
                mobile = user_data[0]['mobile']
                
                #if user is logging in with email and email is not verified then sending email verificationlink again
                if user_data[0]['is_verified'] == False:
                    email_activation_link = settings.EMAIL_ACTIVATION_LINK+user_data[0]['customer_id']
                    send_email_verification_link(user_email, email_activation_link, "resend_email")
                    update_model_obj(User, {'email':user_email}, {'email_otp': get_current_datetime()})
                    user_serializer = User_list_Serializer(User.objects.filter(email= user_email), many=True)
                    return pending_verification_response("Please verify your email. Email verification link has been sent to your registered email address.", data_to_str(user_serializer.data)[0])
            
            #validating email and password for login and sending otp on mobile
            user = authenticate(email=email, password=password)
            if user is not None:
                otp =  str(generate_activation_code())
                send_sms(mobile, otp)
                update_model_obj(User, {'mobile':mobile}, {'otp':otp, 'updated_at':get_current_datetime()})
                user_serializer = User_list_Serializer(User.objects.filter(email=email), many=True)
                return success_response("OTP has been sent on your registered mobile number", data_to_str(user_serializer.data)[0])
            return bad_response("Password is not valid")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

######### Used For Sending/Resending the OTP on all places################################
""" Resend OTP """
class Resend_OTP(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        email = request.data.get('email')
        mobile = request.data.get('mobile')
        new_mobile = request.data.get('new_mobile')
        try:
            if not email and not mobile:
                return bad_response("Please enter email or mobile")   
            otp = str(generate_activation_code())
            if mobile:
                if not is_obj_exists(User, {'mobile':mobile, 'is_superuser':False}):
                    return bad_response("Mobile does not exists!")
                if is_obj_exists(User, {'mobile':mobile, 'is_superuser':False, 'delete':True}):
                    return bad_response("Your account access has been restricted. For assistance, please contact the administrator.")
            else:
                if not is_obj_exists(User, {'email':email, 'is_superuser':False}):
                    return bad_response("Email does not exists!")
                if is_obj_exists(User, {'email':email, 'is_superuser':False, 'delete':True}):
                    return bad_response("Your account access has been restricted. For assistance, please contact the administrator.")
                user_data = get_all_filter_values(User, {'email':email, 'is_superuser':False})
                mobile = user_data[0]['mobile']
            if new_mobile:
                send_sms(new_mobile, otp)
            else:
                send_sms(mobile, otp)
            update_model_obj(User, {'mobile':mobile, 'is_superuser':False}, {'otp':otp, 'updated_at': get_current_datetime()})
            return success_response("OTP has been sent to your registered mobile number.")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        
######### Used For Resending the OTP on all places################################

""" To decode data """
class Decode(APIView):
    renderer_classes=[UserRenderer]
    
    def post(self,request,format=None):
        value = request.data.get('value')
        try:            
            if not value or str(value).strip() == '':
                return bad_response("Please enter value")
            value = value.encode("ascii")
            value = base64.b64decode(value)
            return_value = value.decode("ascii")    
            return success_response(message="success", data={'value':return_value})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

""" Send email to invite user to join remitassure """
class SendInviteEmail(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]
    
    def post(self,request,format=None):
        invite_again = False
        email = request.data.get('email')
        invite_again = request.data.get('invite_again')
        try:
            user_id = request.user.id
            if not email and str(email).strip() == '':
                return bad_response("Please enter email")    
            if is_obj_exists(User, {'email':email, 'is_superuser':False}):
                return bad_response("User with email already exists!")             
            if invite_again == False:
                if is_obj_exists(Invites, {'user_id':user_id, 'email':email}):
                    return bad_response("You have already been invited this user. Do you want to invite this user again?")    
                else:
                    invite_again = True

            #if user want to invite user again 
            if invite_again == True:
                if is_obj_exists(Invites, {'user_id':user_id, 'email':email}):
                    update_model_obj(Invites, {'user_id':user_id, 'email':email}, {'updated_at':get_current_datetime()})
                #sending invite email                
                encoded_referral_code = str(request.user.customer_id).encode("ascii")                 
                encoded_referral_code = base64.b64encode(encoded_referral_code) 
                encoded_referral_code = encoded_referral_code.decode("ascii") 
                link = str(settings.INVITE_LINK)+"?"+str(encoded_referral_code)
                send_invite_email(customer_email=request.user.email, inviter_email=email, link=link)
                create_model_obj(Invites, {'user_id':user_id, 'email':email})
            return success_response("success")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        
""" To check user is activated or disabled """
class Is_User_Exists(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]
    
    def get(self,request,format=None):
        try:
            if is_obj_exists(User, {'id':request.user.id}):
                return success_response("success", data={'is_deleted':request.user.delete})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

""" Activate email with emailed link """
class EmailActivation(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        customer_id = request.data.get('customer_id')
        try:
            if not customer_id or str(customer_id).strip() == '':
                return bad_response("Please enter customer_id")
            if not is_obj_exists(User, {'customer_id':customer_id, 'is_superuser':False}):
                return bad_response("User does not exists!")
            user_data = get_all_filter_values(User, {'customer_id':customer_id, 'is_superuser':False})          
            token_created_at = user_data[0]['email_otp']
            if token_created_at == None or str(token_created_at).strip() == '':
                token_created_at = user_data[0]['created_at']
            else:
                token_created_at = datetime_format(token_created_at)  
            expire_time = token_created_at + EMAIL_ACTIVATION_LINK_EXPIRED
            is_token_expired =  expire_time < timezone.now()
            if is_token_expired:
                return bad_response("Your Email activation link has been expired.")                
            update_model_obj(User, {'customer_id':customer_id, 'is_superuser':False}, {'is_verified':True})
            return success_response(message="Your Email has been verified successfully")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        
""" User profile """
class Profile(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]

    def post(self,request,format=None):
        try:
            profile_completed = True
            serializer = UserProfileSerializer(request.user)
            data = dict(serializer.data)
            if is_obj_exists(User_address, {'user':serializer.data['id']}):
                address = User_address.objects.filter(user_id=serializer.data['id'])
                address_serializer = User_address_list_Serializer(address, many=True)
                data.update(address_serializer.data[0])
            else:
                profile_completed = False
            for key, value in data.items():
                if not value or str(value).strip() == '':
                    if not str(key).lower() in PROFILE_COMPLETED_OPTIONAL_LOWER_FIELDS:
                        profile_completed = False
                    value == ""
            data.update(profile_completed=profile_completed)            
            return success_response("success", data)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

""" Change password """
class ChangePassword(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            old_password = request.data.get('old_password')
            new_password = request.data.get('new_password')
            if not old_password or str(old_password).strip() == '':
                return bad_response('Please enter old password')
            if not new_password or str(new_password).strip() == '':
                return bad_response("Please enter new password")
            user_object = User.objects.get(id=request.user.id)
            if not user_object.check_password(old_password):
                return bad_response("Wrong old password!")
            user_object.set_password(new_password)
            user_object.save()
            return success_response('Password updated successfully')   
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

""" Send reset password OTP """
class SendResetPasswordEmail(APIView):
    renderer_classes=[UserRenderer]
    
    def post(self, request, format=None):
        email = request.data.get('email')
        mobile = request.data.get('mobile')
        if not email and not mobile:
            return bad_response("Please enter email or mobile")
        try:
            otp = str(generate_activation_code())
            #if mobile then send otp on mobile
            if mobile:
                if is_obj_exists(User, {'mobile':mobile, 'is_superuser':False, 'delete':True}):
                    return bad_response("Your account access has been restricted. For assistance, please contact the administrator.")
                if not is_obj_exists(User, {'mobile':mobile, 'is_superuser':False, 'delete':False}):
                    return bad_response("You are not a registered user")
                user = get_all_filter_values(User, {'mobile':mobile, 'is_superuser':False})
                customer_id = user[0]['customer_id']
                send_sms(mobile, otp)
                update_model_obj(User, {'mobile':mobile, 'is_superuser':False}, {'otp':otp, 'updated_at':get_current_datetime()})
                return success_response('OTP has been sent to your mobile.', {'customer_id':customer_id})            
        
            #if email then send otp via email
            if email:
                if is_obj_exists(User, {'email':email, 'is_superuser':False, 'delete':True}):
                    return bad_response("Your account access has been restricted. For assistance, please contact the administrator.")
                if not is_obj_exists(User, {'email':email, 'is_superuser':False, 'delete':False}):
                    return bad_response("You are not a registered user")
                user = get_all_filter_values(User, {'email':email, 'is_superuser':False})

                #if user email is not verified then send email verification link first
                if not user[0]['is_verified']:
                    email_activation_link = settings.EMAIL_ACTIVATION_LINK+user[0]['customer_id']
                    send_email_verification_link(email, email_activation_link, "resend_email")
                    user_serializer = User_list_Serializer(User.objects.filter(email=email, is_superuser=False), many=True)
                    return pending_verification_response("Please verify your email. Email verification link has been sent to your registered email address.", data_to_str(user_serializer.data)[0])
                
                #sending reset otp email
                send_reset_password_email(otp, email)
                update_model_obj(User, {'customer_id':user[0]['customer_id'], 'is_superuser':False}, {'otp':otp, 'updated_at': get_current_datetime()})
                return success_response('OTP has been sent to your email.', {'customer_id':user[0]['customer_id']})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

""" Reset password and verify otp """
class ResetPassword(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        try:
            payload = request.data
            if not 'customer_id' in payload or str(payload['customer_id']).strip() == '':
                return bad_response("Please enter customer id")
            if not 'reset_password_otp' in payload or str(payload['reset_password_otp']).strip() == '':
                return bad_response("Please enter OTP")
            if not 'password' in payload or str(payload['password']).strip() == '':
                return bad_response("Please enter password")
            if is_obj_exists(User, {'customer_id': payload['customer_id'], 'is_superuser':False, 'delete':True}):
                return bad_response("Your account access has been restricted. For assistance, please contact the administrator.")
            if not is_obj_exists(User, {'customer_id': payload['customer_id'], 'is_superuser':False, 'delete':False}):
                return bad_response("User does not exists!")
            if not is_obj_exists(User, {'customer_id': payload['customer_id'], 'otp':payload['reset_password_otp'], 'is_superuser':False}):
                return bad_response("Invalid OTP")

            user_object = User.objects.get(customer_id=payload['customer_id'])
            token_created_at = datetime_format(user_object.updated_at)  
            expire_time = token_created_at + RESET_PASSWORD_TOKEN_EXPIRED
            is_token_expired =  expire_time < timezone.now()
            if is_token_expired:
                return bad_response("OTP expired")      
            user_object.set_password(payload['password'])
            user_object.save()
            list = UserProfileSerializer(User.objects.filter(customer_id=payload['customer_id']), many=True)
            data = dict(list.data[0])
            data['digital_id_verified'] = data['is_digital_Id_verified']
            del data['is_digital_Id_verified']
            update_model_obj(User, {'customer_id':payload['customer_id'], 'is_superuser':False}, {'otp':None})
            return success_response('Password Reset Successfully', data)
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
                
                # #updating tier values in db only during signup first time
                # if not request.user.payment_per_annum:
                #     update_model_obj(User, {'id':user_id}, {'payment_per_annum':request_data['payment_per_annum']})
                # if not request.user.value_per_annum:
                #     update_model_obj(User, {'id':user_id}, {'value_per_annum':request_data['value_per_annum']})

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
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

# class UpdateProfile(APIView): 
#     renderer_classes=[UserRenderer]
#     permission_classes = [IsAuthenticated]
    
#     def post(self, request, format=None):
#         request_data = request.data

#         # User Address Fields
#         flat = request.data.get('flat')
#         building = request.data.get('building')
#         street = request.data.get('street')
#         postcode = request.data.get('postcode')
#         city = request.data.get('city')
#         state = request.data.get('state')
#         country = request.data.get('country')
#         country_code = request.data.get('country_code')

#         USER_FIELDS =['First_name', 'Middle_name', 'Last_name', 'email', 'mobile', 'Date_of_birth', 'Gender', 'location', 'country_code',  'occupation', 'payment_per_annum', 'value_per_annum']
#         USER_ADDRESS_FIELDS =['flat', 'building', 'street', 'postcode', 'city', 'state', 'country' , 'country_code']
#         PROFILE_COMPLETED_OPTIONAL_LOWER_FIELDS = ['middle_name','flat','stripe_customer_id','country_of_birth','is_verified','destination_currency', 'referred_by', 'gender', 'country_of_birth','aml_pep_status']

#         try:
#             user_seriallizer = UserProfileSerializer(request.user)

#             #if KYC / digital_id is not verified then user can update DOB
#             if 'Date_of_birth' in request_data and str(request.user.is_digital_Id_verified).lower() != "approved":
#                 if request_data['Date_of_birth'] != None and str(request_data['Date_of_birth']).strip() != '':
#                     update_model_obj(User, {'id':request.user.id}, {'Date_of_birth':request_data['Date_of_birth']})
            
#             #data_dict = {'First_name':First_name, 'Last_name':Last_name, 'email':email, 'mobile':mobile, 'Gender':Gender, 'building':building, 'street':street, 'postcode':postcode, 'city':city, 'state':state, 'location':location, 'email':email, 'mobile':mobile, "occupation":occupation, 'payment_per_annum':payment_per_annum, 'value_per_annum':value_per_annum}
#             for key in USER_FIELDS:
#                 if str(key).lower() != "middle_name" and str(request.data.get(key)).strip() == '':
#                     key = key.replace("_"," ")
#                     return bad_response(message="Please enter "+key)

#             EMAIL_MOBILE_FIELDS = ['email','mobile']
#             for key in EMAIL_MOBILE_FIELDS:
#                 if request_data.get(key) and is_obj_exists(User,{key: request_data.get(key), 'is_superuser':False, 'delete':False}):
#                     return bad_response(message=key.capitalize()+" already exists!")

#             if 'Middle_name' in request.data and 'First_name' in request.data:
#                 User.objects.filter(id=user_seriallizer.data['id']).update(Middle_name=request_data.get('Middle_name'))
#             elif not 'Middle_name' in request.data and 'First_name' in request.data:
#                 User.objects.filter(id=user_seriallizer.data['id']).update(Middle_name="")

#             user_data = User.objects.get(id=request.user.id)
#             update_serializer = User_Update_Profile_Serializer(user_data, data=request.data, partial=True)
#             if update_serializer.is_valid():
#                 update_serializer.save()
            

#             list_serializer = User_list_Serializer(user_data)
#             dict = list_serializer.data.copy()



#             if not User_address.objects.filter(user_id=user_seriallizer.data['id']).exists():
#                 User_address.objects.create(user_id=user_seriallizer.data['id'])
#             if request_data.get('location'):
#                 User_address.objects.filter(user_id=user_seriallizer.data['id']).update(country=request_data.get('location'))
            
#             #updating flat
#             if 'city' in request.data and 'flat' in request.data:                
#                 User_address.objects.filter(user_id=user_seriallizer.data['id']).update(flat=flat)
#             elif 'city' in request.data and not 'flat' in request.data:                
#                 User_address.objects.filter(user_id=user_seriallizer.data['id']).update(flat="")
#             dict.update(flat=flat)


#             address_data = User_address.objects.filter(user_id=user_seriallizer.data['id'])
#             address_serializer = User_address_Serializer(address_data[0], data=request.data, partial=True)
#             if address_serializer.is_valid():
#                 address_serializer.save()
#                 dict.update(address_serializer.data)
#                 dict['id'] = user_seriallizer.data['id']
#                 for k in dict:
#                     dict[k] = str(dict[k])
#                     if k is None:
#                         dict[k] = ""
#                 return success_response(message="success", data = dict)
#             return bad_response(message=str(address_serializer.errors))
#         except Exception as e:
#                 exc_type, exc_obj, exc_tb = sys.exc_info()
#                 return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

""" FX rate converter """
class ExchangeRateConverter(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        To = request.data.get('to')
        From = request.data.get('from')
        Amount = request.data.get('amount')
        direction = request.data.get('direction')
        if not From or str(From).strip() == '':
            return bad_response("Please enter location" )
        if not To or str(To).strip() == '':
            return bad_response ("Please enter destination")
        if Amount == None or not Amount or str(Amount).strip() == '':
            return bad_response("Please enter amount")
        try:
            default_exchange = None
            From = str(From).strip().upper()
            To = str(To).strip().upper()
            Amount = replace_comma(Amount)
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
            response = Currency_Cloud(From, To, Amount, direction)
            rate = str(response['rate'])
            if str(direction).lower() != "to":
                default_exchange = float(rate) * 100
            return success_response(message="success", data={'amount': comma_value(response['amount']), "rate": comma_value(response['rate']), 'default_exchange':comma_value(default_exchange)})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
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

class DigitalId(APIView):
    renderer_classes = [UserRenderer]
    permission_classes=[IsAuthenticated]
    def post(self, request, format=None):
        try:
            user_serializer = UserProfileSerializer(request.user)
            code = request.data.get("code")
            if not code:
                return bad_response("code is required")

            credentials = settings.DIGITAL_CLIENT_ID+":"+settings.DIGITAL_CLIENT_SECRET
            credentials = credentials.encode("ascii")
            base64_bytes = base64.b64encode(credentials)
            base64_string = base64_bytes.decode("ascii")  
            encoded_token = f"{base64_string}"      

            url = settings.DIGITAL_ID_URL+"/oauth2/token?redirect_uri="+settings.DIGITAL_ID_REDIRECT_URL+"&grant_type=authorization_code&&code="+code
            headers = {'Authorization': 'Basic '+encoded_token}
            response = requests.request("POST", url, headers=headers)
            response = response.json()
            if 'error' in response:
                return bad_response(message = response)
            if 'id_token' in response:
                id_token = response['id_token']
                # data = jwt.decode(id_token, verify=False)
                data = jwt.decode(id_token, options={"verify_signature": False})
                serializer = UserProfileSerializer(request.user)
                User.objects.filter(id = serializer.data['id']).update(is_digital_Id_verified="approved")
                customer_name = str(user_serializer.data['First_name'])+" "+str(user_serializer.data['Last_name'])
                Digital_id_details.objects.create(customer_id=user_serializer.data['customer_id'], customer_name = customer_name,
                                                transaction_id=data['transaction_id'], dob=data['birthdate'],
                                                street=data['address']['street_address'], locality= data['address']['locality'],
                                                region=data['address']['region'],postal_code=data['address']['postal_code'],
                                                country=data['address']['country'], name = data['name'], address_verified= data['digitalid']['address_verified'],
                                                sub = data['sub'], iss= data['iss'], aud= data['aud'], updated_at= data['updated_at'], exp = data['exp'],
                                                iat = data['iat'])
            return success_response(message="success", data=data)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        
""" User KYC details """
class IsDigitalIdVerified(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            verification_status = str(request.user.is_digital_Id_verified)
            return success_response("success", verification_status)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        
""" Veriff API to get session details about user verification status """       
class VeriffSessionDecision(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]

    def post(self,request,format=None):
        try:
            status = None
            session_id = request.data.get('session_id')
            if not session_id:
                return bad_response("Please enter session_id")
            profile_serializer = UserProfileSerializer(request.user)
            secret_key = settings.VERIFF_SECRET_KEY           
            signature = hmac.new(secret_key.encode('utf-8'),session_id.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
            url = settings.VERIFF_URL+"/v1/sessions/"+session_id+"/decision"
            headers = {'Content-Type': 'application/json', 'X-AUTH-CLIENT': settings.VERIFF_API_KEY, 'X-HMAC-SIGNATURE': signature }
            response = requests.request("GET", url, headers=headers)
            response = response.json()
            customer_id = profile_serializer.data['customer_id']
            if not is_obj_exists(Veriff, {'customer_id':customer_id}):
                create_model_obj(Veriff, {'customer_id':customer_id})
            if response['verification'] != None:
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
                if is_obj_exists(Veriff, {'customer_id':customer_id}):
                    update_model_obj(Veriff, {'customer_id':customer_id}, {'first_name':first_name,'last_name':last_name, 'id_type':id_type, 'id_number':id_number,'id_country':id_country, 'ip':ip, 'status':status, 'session_id':session_id, 'reason':reason, 'doc_valid_from':doc_valid_from, 'doc_valid_until':doc_valid_until, 'state':state, 'dob':dob, 'gender':gender, 'updated_at':get_current_datetime(), 'session_id':session_id})
                if str(status).lower() == 'submitted' and User.objects.filter(customer_id=customer_id).exists():
                    User.objects.filter(customer_id=customer_id, is_superuser=False).update(is_digital_Id_verified=str(status).lower())
            #upload media in database
            if HOST == 'LIVE':
                upload_media_in_db(customer_id, session_id)
            return success_response(status, response )
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
  
""" Get and create preferred currency pair for user """
class Preferred_Destination_Currency(APIView):
    renderer_classes = [UserRenderer]
    permission_classes=[IsAuthenticated]

    def post(self, request, format=None):
        try:
            user_id =  request.user.id
            source_currency = request.data.get('source_currency')        
            destination_currency = request.data.get('destination_currency')      

            if not is_obj_exists(User, {'id':user_id, 'is_superuser':False, 'delete':False}):
                return bad_response("User does not exists!") 
            if not destination_currency or str(destination_currency).strip() == '':
                return bad_response("Please enter preferred destination currency")
            if not source_currency or str(source_currency).strip() == '':
                return bad_response("Please enter source destination currency")  
            update_model_obj(User, {'id':user_id}, {'source_currency':str(source_currency).upper(), 'destination_currency':str(destination_currency).upper()})
            data = get_all_filter_values(User, {'id':user_id})
            return success_response("success", {'source_currency':data[0]['source_currency'],'destination_currency':data[0]['destination_currency']})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        
    def get(self, request, format=None):
        try:
            user_id =  request.user.id
            if not is_obj_exists(User, {'id':user_id, 'is_superuser':False, 'delete':False}):
                return bad_response("User does not exists!") 
            data = get_all_filter_values(User, {'id':user_id})
            return success_response("success", {'source_currency':data[0]['source_currency'],'destination_currency':data[0]['destination_currency']})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

"""" Get FX rate from database """
def forex_currency(From, To, Amount, direction):
    try:
        reverse_rate = 0
        if is_obj_exists(forex, {'source_currency':To, 'destination_currency':From}):
            forex_obj = forex.objects.get(source_currency=To, destination_currency=From,is_enabled=True)
            rate = 1 / Decimal(forex_obj.rate) 
        else:
            forex_obj = forex.objects.get(source_currency=From, destination_currency=To,is_enabled=True)
            rate = Decimal(replace_comma(forex_obj.rate))
            reverse_rate = 1 / rate
        if direction == 'To':
            amount = Decimal(Amount) * Decimal(reverse_rate)
        else:
            amount = Decimal(Amount) * Decimal(rate)
        rate = math.floor(rate * 100) / 100
        amount = math.floor(amount * 100) / 100
        # markup = Decimal(Amount) * Decimal(forex_obj.markup)
        # markup = Decimal(amount) / 100
        # amount = Decimal(amount) + Decimal(forex_obj.markup)
    except ObjectDoesNotExist:
        amount = Decimal(0)
        rate = Decimal(0)
    return {'amount': amount, 'rate': rate}

""" Get FX rate with currency cloud """
def Currency_Cloud(From, To, Amount, direction):
    try:
        # url1 = settings.CC_URL+"/authenticate/api"
        # m = MultipartEncoder(fields={'login_id': settings.LOGIN_ID, 'api_key': settings.CC_API_KEY})
        # headers = {'Content-Type': m.content_type}
        # response = requests.request("POST", url1, data=m, headers=headers)
        # response = response.json()
        # auth_token = response['auth_token']
        # url2 = settings.CC_URL+"/rates/detailed?buy_currency="+To+"&sell_currency="+From+"&fixed_side=sell&amount="+Amount+"&conversion_date_preference=optimize_liquidity"
        # headers = {'X-Auth-Token': auth_token, 'Accept': 'application/json'}
        # response2 = requests.request("GET", url2, headers=headers)
        # response2 = response2.json() 
        # print(response2)
        # if 'client_rate' in response2:
        #     client_rate = response2['client_rate']
        #     client_buy_amount = response2['client_buy_amount']      
        #     if '.' in client_rate:
        #         client_rate = float(client_rate)
        #     else:
        #         client_rate = int(client_rate)
        #     if '.' in client_buy_amount:
        #         client_buy_amount = float(client_buy_amount)
        #     else:
        #         client_buy_amount = int(client_buy_amount)
        #     amount = client_buy_amount
        #     rate = client_rate
        # elif 'error_code' in response2:
        forex_data = forex_currency(From, To, Amount, direction)
        amount = forex_data['amount']
        # if '.' in str(amount):
        #     amount = str(round(float(amount),2))
        rate = forex_data['rate']
        return {'amount': amount, 'rate': rate}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
        error_logs(file_content)
        return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

""" Delete user from DB """
class ContactUsView(APIView):

    def post(self, request, format=None):
        try:
            fields = ['name','email','message']
            payload = request.data
            #validation
            for k in fields:
                if not k in payload or str(k).strip() == '' or k == None:
                    return bad_response(str(k)+" is required")
            response = send_contact_us_email(payload)
            if response['code'] == 400:
                return bad_response(response['message'])
            Contact_us.objects.create(name=payload['name'], email=payload['email'], message=payload['message'], status="pending")
            return success_response(message="success", data=None)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        
############################ Update Tiers Request ################################
""" Send Tier Value To Customer and RemitAssure """
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
        

############################### Testing Views/Functions for Developer #############
""" Delete user from DB """
class DeleteUser(APIView):
    renderer_classes=[UserRenderer]

    @csrf_exempt
    def delete(self, request, pk, format=None):
        try:
            if not User.objects.filter(id=pk, delete=False).exists():
                return bad_response(message="User does not exist")
            user = User.objects.filter(id=pk)
            user_obj = get_object_or_404(User, id=pk)
            if Recipient.objects.filter(user_id=pk).exists():
                recipients = Recipient.objects.filter(user_id=pk)
                if Recipient_bank_details.objects.filter(recipient_id__in=recipients).exists():
                    bank = Recipient_bank_details.objects.filter(recipient_id__in=recipients)
                    bank.delete()
                recipients.delete()
            if User_address.objects.filter(user_id=pk).exists():
                address = User_address.objects.filter(user_id=pk)
                address.delete()
            if Transaction_details.objects.filter(customer_id=user_obj.customer_id).exists():
                transactions = Transaction_details.objects.filter(customer_id=user_obj.customer_id)
                transactions.delete()
            if zai_agreement_details.objects.filter(zai_email=user_obj.email).exists():
                agreements = zai_agreement_details.objects.filter(zai_email=user_obj.email)
                agreements.delete()
            if zai_payid_details.objects.filter(zai_email=user_obj.email).exists():
                payid = zai_agreement_details.objects.filter(zai_email=user_obj.email)
                payid.delete()
            user.delete()
            return success_response(message="User deleted successfully", data=None)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/views"
            error_logs(file_content)
            return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))
        
