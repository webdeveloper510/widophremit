from Widoph_Remit.package import *
from .sendsms import *
from .model_queries import *
from Widoph_Remit.helpers import success_logs, error_logs
from django.core.files.base import ContentFile

def replace_(key):
    return str(key).replace("_"," ")

def replace_comma(key):
    return str(key).replace(",","")

def get_current_datetime():
    return timezone.now()

def update_registration_otp(mobile, otp):
    try:
        if is_obj_exists(Registration_otp, {'mobile':mobile}):
            update_model_obj(Registration_otp, {'mobile':mobile}, {'otp':otp, 'created_at':get_current_datetime()})
        else:
            create_model_obj(Registration_otp, {'mobile':mobile, 'otp':otp})
        # Used for sending sms to the mobile number
        send_sms(mobile, otp)
        return {'code':200}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/helpers"
        error_logs(file_content)
        return {'code':400, 'message':str(e)+" in "+str(exc_tb.tb_lineno)}

def is_registration_token_expired(created_at):
    try:
        expire_time = created_at + settings.MOBILE_VERIFICATION_TOKEN_EXPIRED
        return expire_time < timezone.now()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/helpers"
        error_logs(file_content)
        return file_content
    
def creating_invitation_coupons(referred_by, user):
    try:
        if is_obj_exists(referral_type, {'type':referral_dict['invite']}):
            referral_type_id = filter_model_objs(referral_type, {'type':referral_dict['invite']}, {'id'})
            referral_data = filter_model_objs(referral, {'referral_type_id':referral_type_id[0]['id']}, {'id','referred_by_amount','referred_to_amount'})
            if not is_obj_exists(referral_meta, {'user_id':user['id'], 'referral_id':referral_data[0]['id'], 'referred_by':referred_by}):               
                create_model_obj(referral_meta, {'user_id':user['id'], 'referral_id':referral_data[0]['id'], 'referred_by':referred_by, 'claimed':False, 'is_used':False, 'discount':referral_data[0]['referred_to_amount']})               
            #saving instance for referred to    
            if not is_obj_exists(referral_meta, {'user_id':referred_by, 'referral_id':referral_data[0]['id'], 'referred_to':user['id']}):
                create_model_obj(referral_meta, {'user_id':referred_by, 'referral_id':referral_data[0]['id'], 'referred_to':user['id'], 'claimed':False, 'is_used':False, 'discount': referral_data[0]['referred_by_amount']})               
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/helpers"
        error_logs(file_content)
        return False

def data_to_str(data=None):
    if data is not None:
        return  [{key: str(value) if value is not None else '' for key, value in entry.items()} for entry in data]
    return []

def data_to_none_str(data=None):
    if data is not None:
        return  [{key: str(value) if value != None and str(value).strip() != '' else None for key, value in entry.items()} for entry in data]
    return []

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        # 'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def generate_activation_code():
    code = int(''.join([str(random.randint(0,9)) for _ in range(6)]))
    if len(str(code)) != 6:
        code = str(''.join([str(random.randint(0,9)) for _ in range(1)]))
        code = code.ljust(6, code)
    return code

def is_mobile_token_expired(created_at):
    expire_time = created_at+settings.MOBILE_VERIFICATION_TOKEN_EXPIRED
    is_token_expired =  expire_time < get_current_datetime()
    return is_token_expired

def datetime_format(value):
    return parser.parse(str(value))  

def str_to_date(data):
    date_object = parser.parse(str(data))
    return date_object.date()

def create_invite_coupons(user_id, referred_by):
    try:
        if referral_type.objects.filter(type=referral_dict['invite']).exists():
            referral_type_id = referral_type.objects.filter(type=referral_dict['invite']).values('id')
            referral_data = referral.objects.filter(referral_type_id=referral_type_id[0]['id'], currency="AUD").values('id','referred_by_amount','referred_to_amount')
            if not referral_meta.objects.filter(user_id=user_id, referral_id=referral_data[0]['id'], referred_by=referred_by).exists():               
                referral_meta.objects.create(user_id=user_id, referral_id=referral_data[0]['id'],referred_by=referred_by, claimed=False, is_used=False, discount=referral_data[0]['referred_to_amount'])               
            #saving instance for referred to    
            if not referral_meta.objects.filter(user_id=referred_by, referral_id=referral_data[0]['id'], referred_to=user_id).exists():
                referral_meta.objects.create(user_id=referred_by, referral_id=referral_data[0]['id'], referred_to=user_id, claimed=False, is_used=False, discount= referral_data[0]['referred_by_amount'])               
            return True
        return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/helpers"
        error_logs(file_content)
        return False

def expire_time(type):
    try:
        expire_time = None
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
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/helpers"
        error_logs(file_content)
        return file_content
    
def create_referral_code(email, customer_id):
    try:
        name = str(re.split('@', email)[0]).upper().strip()
        customer_id = str(customer_id).replace(str(customer_id)[:2],'')
        total_length = 6
        n_len = 4
        c_length = total_length - n_len
        if len(name) < 4:
            n_len = len(name) # 1
            c_length = total_length-n_len # 5 
        referral_code = str(name)[:n_len] + str(customer_id)[:c_length]
        if User.objects.filter(referral_code=referral_code).exists():
            create_referral_code(email, customer_id)
        return referral_code
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/helpers"
        error_logs(file_content)
        return None
    
def create_customer_id(email, country_code, id):
    try:
        length = 6
        random_digits = [str(random.randint(0, 9)) for _ in range(length)]
        random_digits = ''.join(random_digits)
        random_digits = int(random_digits[:-len(str(id))])
        customer_id = str(country_code)+str(random_digits)+str(id)
        if User.objects.filter(customer_id=customer_id, is_superuser=False).exists():
            customer_id =  create_customer_id(email, country_code, id)
        return customer_id
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/helpers"
        error_logs(file_content)
        return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

def create_customer_id_and_referral_code(email, country_code, id):
    try:
        customer_id = create_customer_id(email, country_code, id)
        ref_code = create_referral_code(email=email, customer_id=customer_id)
        if not User.objects.filter(referral_code=ref_code).exists():
            return {'customer_id': customer_id, 'referral_code': ref_code}
        else:
            return create_customer_id_and_referral_code(email, country_code, id)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/helpers"
        error_logs(file_content)
        return bad_response(message=str(e) + " in line " + str(exc_tb.tb_lineno))

def generate_veriff_signature(session_id):
    secret_key = settings.VERIFF_SECRET_KEY         
    signature = hmac.new(secret_key.encode('utf-8'),session_id.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    return signature

def get_media_from_veriff(session_id):
    try:
        url = settings.VERIFF_URL+"/v1/sessions/"+session_id+"/media"
        signature = generate_veriff_signature(session_id)           
        headers = {'Content-Type': 'application/json', 'X-AUTH-CLIENT': settings.VERIFF_API_KEY, 'X-HMAC-SIGNATURE': signature }
        response = requests.request("GET", url, headers=headers)
        response = response.json()
        return response            
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/helpers"
        error_logs(file_content)
        return False
    
def download_veriff_media(media_id):
    try:
        url = settings.VERIFF_URL+"/v1/media/"+media_id
        signature = generate_veriff_signature(media_id)           
        headers = {'Content-Type': 'application/json', 'X-AUTH-CLIENT': settings.VERIFF_API_KEY, 'X-HMAC-SIGNATURE': signature }
        response = requests.request("GET", url, headers=headers)
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/helpers"
        error_logs(file_content)
        return False
    
def upload_media_in_db(customer_id, session_id):
    try:
        response = get_media_from_veriff(session_id)
        if response and response['status'] == 'success': 
            if 'images' in response and response['images']:
                for x in response['images']:
                    image = download_veriff_media(x['id'])
                    if image and not is_obj_exists(Veriff_media, {'customer_id':customer_id, 'media_id':x['id']}):
                        obj = Veriff_media.objects.create(customer_id=customer_id, session_id=session_id, media_id=x['id'], name=x['name'], type='image')
                        obj.image.save(f"{x['name']}.{x['mimetype'].split('/')[-1]}", ContentFile(image.content))
                        obj.save()
                        
            if 'videos' in response and response['videos']:
                for x in response['videos']:
                    video = download_veriff_media(x['id'])
                    if video and not is_obj_exists(Veriff_media, {'customer_id':customer_id, 'media_id':x['id']}):
                        obj = Veriff_media.objects.create(customer_id=customer_id, session_id=session_id, media_id=x['id'], name=x['name'], type='video')
                        obj.video.save(f"{x['name']}.{x['mimetype'].split('/')[-1]}", ContentFile(video.content))
                        video_content = ContentFile(b"".join(chunk for chunk in video.iter_content(chunk_size=1024)))
                        obj.video.save(x['mimetype']+".mp4", video_content)
                        obj.save()
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in auth_app/helpers"
        error_logs(file_content)
        return False    