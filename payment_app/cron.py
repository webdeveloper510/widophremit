from .models import Transaction_details
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from .helper import CreateCronJobFile, CreateErrorFile
import logging
import sys
from auth_app.emails import send_otp_email
from Widoph_Remit.helpers import error_logs
from auth_app.helpers import generate_activation_code
from auth_app.models import OTP_history
from datetime import datetime, timedelta

transaction = settings.TRANSACTION

def expire_transactions():
    try:
        two_days_ago = timezone.now() - timedelta(days=2)
        incomplete_payments = Transaction_details.objects.filter(payment_status="incomplete", updated_at__lt=two_days_ago)

        for x in incomplete_payments:
            #x.payment_status = "Expired"
            Transaction_details.objects.filter(id=x.id).update(payment_status=transaction['expired'])
            #x.updated_at = timezone.now()
            #x.save()
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        CreateCronJobFile
        CreateCronJobFile(f"{str(e)} in line {str(exc_tb.tb_lineno)} in payment_app/cronjob")
        return False


def otp_email():
    try:
        obj = OTP_history.objects.all().last()
        otp = int(generate_activation_code())
        if not obj:
            OTP_history.objects.create(new_otp=otp)
        else:
            if obj.created_at < datetime.now() - timedelta(days=7):
                send_otp_email(otp)
                OTP_history.objects.create(new_otp=otp, old_otp=obj.new_otp)            
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        CreateCronJobFile(f"{str(e)} in line {str(exc_tb.tb_lineno)} in payment_app/cronjob")
        return False

# python manage.py shell
# from payment_app.cronjob import expire_transactions
# expire_transactions()

