from Widoph_Remit.package import *
import calendar
from dateutil import parser
from Widoph_Remit.helpers import error_logs, success_logs

def referral_birthday(user_id, dob):
    try:
        if dob is None:
            data = User.objects.filter(id=user_id, is_superuser=False).values('id','Date_of_birth')
            dob = data[0]['Date_of_birth']
            user_id = data[0]['id']
        if str(dob[5]) == "0":
            month = str(dob[6])
        else:
            month = str(dob[5])+str(dob[6])
        if str(month) == str(datetime.now().month):
            if referral.objects.filter(name=referral_dict['birthday']).exists():
                data = referral.objects.filter(name=referral_dict['amount']).values('start_date','end_date','status','id')
                if str(data[0]['status']) == "active":
                    start_date = parser.parse( str(data[0]['start_date']) )
                    end_date =parser.parse( str(data[0]['end_date']) )
                    if datetime.now().date() > start_date.date() or datetime.now().date() == start_date.date():
                        if datetime.now().date() < end_date.date() or datetime.now().date() == end_date.date():
                            referral_id = data[0]['id']
                            referral_meta.objects.create(user_id=user_id, referral_id=referral_id)  
                        return True
            return False
        else:           
            # month_name = calendar.month_name[int(month)]
            # current_month = datetime.now().month
            # current_month_name = calendar.month_name[int(month)]
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/referrals"
        error_logs(file_content)
        return False
    
def referral_amount(user_id, transaction_id):
    try:
        format = '%Y-%m-%d'
        if not Transaction_details.objects.filter(transaction_id=transaction_id).exists():
            return False
        if referral.objects.filter(name=referral_dict['amount']).exists():
            data = referral.objects.filter(name=referral_dict['amount']).values('start_date','end_date','status','id')
            if str(data[0]['status']) == "active":
                start_date = parser.parse( str(data[0]['start_date']) )
                end_date = parser.parse( str(data[0]['end_date']) )
                if datetime.now().date() > start_date.date() or datetime.now().date() == start_date.date():
                    if datetime.now().date() < end_date.date() or datetime.now().date() == end_date.date():
                        referral_id = data[0]['id']
                        referral_meta.objects.create(user_id=user_id, transaction_id=transaction_id, referral_id=referral_id)  
                    return True
            return False
        return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/referrals"
        error_logs(file_content)
        return False 
    
def referral_festivals(user_id):
    try:
        format = '%Y-%m-%d'
        if not referral_type.objects.filter(type=referral_dict['festival']).exists():
            return False
        type = referral_type.objects.filter(type=referral_dict['festival']).values('id')
        referral_type_id = type[0]['id']
        if not referral.objects.filter(referral_type_id=referral_type_id).exists():
            return False
        data = referral.objects.filter(referral_type_id=referral_type_id).values('start_date','end_date','status','id')
        for i in data:
            if str(i['status']) == "active":
                start_date = parser.parse(str(i['start_date']))
                end_date = parser.parse(str(i['end_date']))
                if datetime.now().date() > start_date.date() or datetime.now().date() == start_date.date():
                    if datetime.now().date() < end_date.date() or datetime.now().date() == end_date.date():
                        referral_meta.objects.create(user_id=user_id, referral_id=i['id'])  
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in payment_app/referrals"
        error_logs(file_content)
        return False