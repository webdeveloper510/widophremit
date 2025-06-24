from Remit_Assure.package import *
from auth_app.sendsms import *
from .model_queries import *
from .helpers import *

""" email template images """
def email_template_image():
    try:
        image_data = Email_template_images.objects.all().values('title','image')
        images = []
        image_dict = {}
        for x in image_data:
            dict = {x['title']: settings.BASE_URL+"/media/"+x['image']}
            image_dict.update(dict)
        return image_dict
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in auth_app/emails"
        error_logs(file_content)
        return {}
    
""" sending email with credentials """
def send_email(html_content, msg):
    try:
        html_content = html_content
        msg = msg
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.quit()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in auth_app/emails"
        error_logs(file_content)
    
""" sending notifications via email to RemitAssure """
def email_to_RA(type, id):
    try:
        if settings.SEND_EMAIL == True:
            image_dict = email_template_image()   
            if type == "customer" and User.objects.filter(id=id).exists():
                data = User.objects.filter(id=id).values('email','customer_id','location','mobile','created_at')[0]
                data['created_at'] = str_to_date(data['created_at'])
                message = "New customer with "+data['email']+" has signed up."
                html_content = render_to_string('new_user.html', {'type':"customer",'data':image_dict, 'message':message, 'customer':data})
            
            elif type == "transaction" and Transaction_details.objects.filter(transaction_id=id).exists():
                data = Transaction_details.objects.filter(transaction_id=id).values('customer_id', 'payment_status','transaction_id','recipient_name','send_currency', 'receive_currency','amount', 'receive_amount','date', 'reason', 'exchange_rate', 'recipient','customer_id','send_method','total_amount','discount_amount','updated_at')[0]
                comma =  comma_separated(send_amount=data['amount'], receive_amount=data['receive_amount'], exchange_rate=data['exchange_rate'])
                comma2 =  comma_separated(send_amount=data['total_amount'], receive_amount=data['discount_amount'], exchange_rate=data['discount_amount'])
                data['total_amount'] = comma2['send_amount']
                data['discount_amount'] = comma2['receive_amount']
                data['amount'] = comma['send_amount']
                data['receive_amount'] = comma['receive_amount']
                data['exchange_rate'] = comma['exchange_rate']
                if User.objects.filter(customer_id=data['customer_id']).exists():
                    user_obj = User.objects.filter(customer_id=data['customer_id']).values('email')[0]
                    message = "Customer with "+user_obj['email']+" email has created a new transaction."
                else:
                    message = "Customer with "+data['customer_id']+" Cust Id has created a new transaction."
                html_content = render_to_string('admin_transaction_notification.html', {'type':"transaction",'data':image_dict, 'message':message, 'transaction':data})
            elif type == "webhook_transaction" and Transaction_details.objects.filter(transaction_id=id).exists():
                data = Transaction_details.objects.filter(transaction_id=id).values('customer_id', 'payment_status','transaction_id','recipient_name','send_currency', 'receive_currency','amount', 'receive_amount','date', 'reason', 'exchange_rate', 'recipient','customer_id','send_method','total_amount','discount_amount','updated_at')[0]
                comma =  comma_separated(send_amount=data['amount'], receive_amount=data['receive_amount'], exchange_rate=data['exchange_rate'])
                comma2 =  comma_separated(send_amount=data['total_amount'], receive_amount=data['discount_amount'], exchange_rate=data['discount_amount'])
                data['total_amount'] = comma2['send_amount']
                data['discount_amount'] = comma2['receive_amount']
                data['amount'] = comma['send_amount']
                data['receive_amount'] = comma['receive_amount']
                data['exchange_rate'] = comma['exchange_rate']
                message = "New Updated Payment Status"
                html_content = render_to_string('admin_transaction_notification.html', {'type':"webhook_transaction",'data':image_dict, 'message':message, 'transaction':data})
            html_content = html_content
            msg = EmailMultiAlternatives(
                subject='Notification From Widoph Remit',
                from_email= settings.EMAIL_HOST_USER,
                to=[str(settings.REMIT_ASSURE_EMAIL)],
            )
            send_email(html_content, msg)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in auth_app/emails"
        error_logs(file_content)
    
""" sending  or resending email verification link """
def send_email_verification_link(email, otp, type):
    try:
        if settings.SEND_EMAIL == True:
            image_dict = email_template_image()
            if type == "email":
                html_content = render_to_string('verifyemail.html',{'otp':otp, 'data':image_dict, 'expire_time':expire_time(type="email")})
            elif type == "resend_email":
                html_content = render_to_string('resend_verify_email.html',{'otp':otp, 'data':image_dict, 'expire_time':expire_time(type="email")})
            msg = EmailMultiAlternatives(
                subject='Email Verification Link',
                body='Email Verification Link',
                from_email= settings.EMAIL_HOST_USER,
                to=[email],
            )
            send_email(html_content, msg)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in auth_app/emails"
        error_logs(file_content)
    
""" sending email to persong who referred the customer """
def send_referred_by_email(email, user_email):
    try:
        if settings.SEND_EMAIL == True:
            image_dict = email_template_image()
            html_content = render_to_string('referral-signup.html',{'email':user_email, 'data':image_dict})
            msg = EmailMultiAlternatives(
                subject='From RemitAssure',
                body='Congratulations! Your friend has signed up with your refferal code',
                from_email= settings.EMAIL_HOST_USER,
                to=[email],
                    )
            send_email(html_content, msg)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in auth_app/emails"
        error_logs(file_content)
    
""" sending welcome email """
def send_welcome_email(email):
    try:
        if settings.SEND_EMAIL == True :
            image_dict = email_template_image()              
            html_content = render_to_string('welcome.html', {'data':image_dict,'home':settings.HOME_LINK, 'support':settings.SUPPORT_CENTER_LINK, 'unsubscribe':settings.UNSUBSCRIBE_LINK, 'remitassure':settings.REMITASSURE_LINK})
            msg = EmailMultiAlternatives(
                subject='Welcome to Widoph Remit',
                body='Welcome to Widoph Remit',
                from_email= settings.EMAIL_HOST_USER,
                to=[email],
            )
            send_email(html_content, msg)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in auth_app/emails"
        error_logs(file_content)
    
""" Send email to invite user to join remitassure """
def send_invite_email(customer_email, inviter_email, link):
    try:
        if settings.SEND_EMAIL == True:
            image_dict = email_template_image()               
            html_content = render_to_string('referral.html', {'data':image_dict,'customer_email':customer_email, 'link':link})
            html_content = html_content
            msg = EmailMultiAlternatives(
                subject='Your Friend has invited you',
                from_email= settings.EMAIL_HOST_USER,
                to=[str(inviter_email)],
            )
            send_email(html_content, msg)            
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in auth_app/emails"
        error_logs(file_content)
    
""" send reset password otp via email """
def send_reset_password_email(otp, email):
    try:
        if settings.SEND_EMAIL ==  True:
            image_dict = email_template_image()  
            html_content = render_to_string('Forgotpassword.html',{'otp':otp, 'data':image_dict, 'expire_time':expire_time(type="reset_password")})
            msg = EmailMultiAlternatives(
                subject='Reset your password',
                body='Reset Password OTP',
                from_email= settings.EMAIL_HOST_USER,
                to=[email],
            )
            send_email(html_content, msg)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in auth_app/emails"
        error_logs(file_content)
    
""" Send Contact us email to RA """
def send_contact_us_email(payload):
    try:
        if settings.SEND_EMAIL == True:
            image_dict = email_template_image()
            html_content = render_to_string('contact_us.html',{'date':get_current_date(),'email':payload['email'],'name':payload['name'],'message':payload['message'],'data':image_dict})
            msg = EmailMultiAlternatives(
                subject='Email From RemitAssure',
                body='',
                from_email= settings.EMAIL_HOST_USER,
                to=[settings.REMIT_ASSURE_EMAIL],
            )
            send_email(html_content, msg)
        return {'code':200}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in auth_app/emails"
        error_logs(file_content)
        return {'code':400, 'message':str(e)}
    
""" sending update tier request email to RA """
def send_update_tier_email_to_RA(user_data, item):
    print("send email 11111111111111111111111111",SEND_EMAIL)
    try:
        if SEND_EMAIL:
            image_dict = email_template_image()
            html_content = render_to_string('update_tier_request_ra.html',{'item':item, 'user':user_data, 'data':image_dict})
            msg = EmailMultiAlternatives(
                subject='Update Tier Request',
                body='Update Tier Request from customer',
                from_email= settings.EMAIL_HOST_USER,
                to=[settings.REMIT_ASSURE_EMAIL],
            )
            send_email(html_content, msg)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in auth_app/emails"
        print(file_content)
        error_logs(file_content)
    
""" sending update tier request email to customer """
def send_update_tier_email_to_customer(user_data, item):
    try:
        if SEND_EMAIL:
            print("send_email 222222222222222222222")
            image_dict = email_template_image()
            html_content = render_to_string('update_tier_request_customer.html', {'ra_email':settings.REMIT_ASSURE_EMAIL, 'item':item, 'user':user_data, 'data':image_dict})
            msg = EmailMultiAlternatives(
                subject='Requested To Update Tier',
                body='Update Tier Request To RemitAssure',
                from_email= settings.EMAIL_HOST_USER,
                to=[user_data['email']],
            )
            send_email(html_content, msg)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in auth_app/emails"
        print(file_content)
        error_logs(file_content)
    
""" send veriff email to RA  """
def send_veriff_email(user_data):
    try:
        if SEND_EMAIL:
            image_dict = email_template_image()
            html_content = render_to_string('veriff_email.html', {'user':user_data, 'data':image_dict})
            msg = EmailMultiAlternatives(
                subject='New KYC Request',
                body='New user KYC request submitted',
                from_email= settings.EMAIL_HOST_USER,
                to=['REMIT_ASSURE_EMAIL'],
            )
            send_email(html_content, msg)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in auth_app/emails"
        print(file_content)
        error_logs(file_content)
    