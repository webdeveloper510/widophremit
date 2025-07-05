from django.db import models
from auth_app.models import *


class currencies(models.Model):
    type = models.CharField(max_length=300, null=True, blank=True)
    country = models.CharField(max_length=300, null=True, blank=True)
    currency =  models.CharField(max_length=300, null=True, blank=True)
    currency_symbol =  models.CharField(max_length=300, null=True, blank=True)
    phone_code =  models.CharField(max_length=300, null=True, blank=True)
    country_code =  models.CharField(max_length=300, null=True, blank=True)
    status =  models.CharField(max_length=300, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
           verbose_name_plural = "RemitAssure Currencies List"


class Recipient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=250, null=True, blank=True)
    middle_name = models.CharField(max_length=250, null=True, blank=True)
    last_name = models.CharField(max_length=250, null=True, blank=True)
    email = models.EmailField(verbose_name='Email', max_length=200, null=True, blank=True)
    mobile = models.CharField(max_length=250, null=True, blank=True)
    flat = models.CharField(max_length=250, null=True, blank=True)
    building = models.CharField(max_length=250, null=True, blank=True)
    street = models.CharField(max_length=300, null=True, blank=True)
    postcode = models.CharField(max_length=30, null=True, blank=True)
    city = models.CharField(max_length=250 , null=True, blank=True)
    state = models.CharField(max_length=250, null=True, blank=True)
    country_code = models.CharField(max_length=250, null=True, blank=True)
    country = models.CharField(max_length=250, null=True, blank=True)
    update_profile = models.CharField(max_length=90, null=True, blank=True)
    transfer_now = models.CharField(max_length=90, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    delete = models.BooleanField(default=False)

    account_type = models.CharField(max_length=250, null=True, default="individual")
   
    def __str__(self):
        return "{}".format(self.id)

    class Meta:
           verbose_name_plural = "Recipient"

class Recipient_bank_details(models.Model):
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=90)
    account_name = models.CharField(max_length=90)
    account_number = models.CharField(max_length=90)
    swift_code = models.CharField(max_length=90, null=True, blank=True)
    bank_address = models.TextField(max_length=300, null=True, blank=True)
    delete = models.BooleanField(default=False)

    class Meta:
           verbose_name_plural = "Recipient Bank Details"

class Recipient_business_details(models.Model):
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=25,null=True, blank=True)
    business_nature = models.CharField(max_length=25,null=True, blank=True)
    registration_date = models.CharField(max_length=90,null=True, blank=True)
    registration_number = models.CharField(max_length=25,null=True, blank=True)
    registration_country = models.CharField(max_length=250,null=True, blank=True)
    business_address = models.CharField(max_length=300,null=True, blank=True)
    delete = models.BooleanField(default=False)

    class Meta:
           verbose_name_plural = "Recipient Business Details"



class Transaction_details(models.Model):
    customer_id = models.CharField(max_length=90)
    aml_pep_status = models.CharField(max_length=90, null=True, blank=True)
    recipient = models.CharField(max_length=90)
    recipient_name = models.CharField(max_length=90)
    send_currency = models.CharField(max_length=90)
    receive_currency = models.CharField(max_length=90)
    amount = models.CharField(max_length=90)
    total_amount = models.CharField(max_length=90)
    receive_amount = models.CharField(max_length=90, null=True, blank=True)
    send_method = models.CharField(max_length=90, null=True, blank=True)
    receive_method = models.CharField(max_length=90, null=True, blank=True)
    payout_partner = models.CharField(max_length=300, null=True, blank=True)
    exchange_rate = models.CharField(max_length=90, null=True, blank=True)
    tm_status = models.CharField(max_length=90)
    rule = models.CharField(max_length=200, null=True, blank=True)
    payment_status = models.CharField(max_length=90)
    payment_status_reason = models.CharField(max_length=90)
    transaction_id = models.CharField(max_length=90, null=True, blank=True)
    reason = models.CharField(max_length=200, null=True, blank=True)
    card_token = models.CharField(max_length=200, null=True, blank=True)
    card_type = models.CharField(max_length=120)
    tm_label = models.CharField(max_length=320)
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    risk_score = models.CharField(max_length=30)
    risk_group = models.CharField(max_length=30)
    payment_gateway_transaction_id = models.CharField(max_length=250)
    agreement_id = models.CharField(max_length=250, blank=True, null=True)
    discount_amount = models.CharField(max_length=250, blank=True, null=True)
    paid_amount = models.CharField(max_length=250, blank=True, null=True)
    app_version = models.CharField(max_length=250, blank=True, null=True)
    platform =models.CharField(max_length=250, blank=True, null=True)
    currency = models.ForeignKey(currencies, on_delete=models.PROTECT, null=True, blank=True )

    class Meta:
           verbose_name_plural = "Transaction Details"


class Transaction_details_dump(models.Model):
    customer_id = models.CharField(max_length=90)
    aml_pep_status = models.CharField(max_length=90, null=True, blank=True)
    recipient = models.CharField(max_length=90)
    recipient_name = models.CharField(max_length=90)
    send_currency = models.CharField(max_length=90)
    receive_currency = models.CharField(max_length=90)
    amount = models.CharField(max_length=90)
    total_amount = models.CharField(max_length=90)
    receive_amount = models.CharField(max_length=90, null=True, blank=True)
    send_method = models.CharField(max_length=90, null=True, blank=True)
    receive_method = models.CharField(max_length=90, null=True, blank=True)
    payout_partner = models.CharField(max_length=300, null=True, blank=True)
    exchange_rate = models.CharField(max_length=90, null=True, blank=True)
    tm_status = models.CharField(max_length=90)
    rule = models.CharField(max_length=200, null=True, blank=True)
    payment_status = models.CharField(max_length=90)
    payment_status_reason = models.CharField(max_length=90)
    transaction_id = models.CharField(max_length=90, null=True, blank=True)
    reason = models.CharField(max_length=200, null=True, blank=True)
    card_token = models.CharField(max_length=200, null=True, blank=True)
    card_type = models.CharField(max_length=120)
    tm_label = models.CharField(max_length=320)
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    risk_score = models.CharField(max_length=30)
    risk_group = models.CharField(max_length=30)
    payment_gateway_transaction_id = models.CharField(max_length=250)
    agreement_id = models.CharField(max_length=250, blank=True, null=True)
    discount_amount = models.CharField(max_length=250, blank=True, null=True)
    paid_amount = models.CharField(max_length=250, blank=True, null=True)
    app_version = models.CharField(max_length=250, blank=True, null=True)
    platform =models.CharField(max_length=250, blank=True, null=True)
    
    class Meta:
           verbose_name_plural = "Transaction Details Dump"


class stripe_card_details(models.Model):
    customer_id =  models.CharField(max_length=90)
    name = models.CharField(max_length = 150)
    card_number = models.CharField(max_length = 150)
    expiry_month = models.CharField(max_length = 150)
    expiry_year = models.CharField(max_length = 150)
    card_token = models.CharField(max_length = 150)
    card_id = models.CharField(max_length = 150)

    class Meta:
           verbose_name_plural = "Card Details"


class stripe_card_token(models.Model):
    customer_id =  models.CharField(max_length=90)
    name = models.CharField(max_length = 150)
    card_token = models.CharField(max_length = 150)
    card_id = models.CharField(max_length = 150)
    class Meta:
           verbose_name_plural = "Stripe Card Token"


class send_currency_list(models.Model):
    currency =  models.CharField(max_length=90)
    country = models.CharField(max_length = 150)
    class Meta:
        verbose_name_plural = "Send Currency List"

class receive_currency_list(models.Model):
    currency =  models.CharField(max_length=90)
    country = models.CharField(max_length = 150)
    class Meta:
        verbose_name_plural = "Receive Currency List"

class forex(models.Model):
    source_currency =  models.CharField(max_length=90)
    destination_currency =  models.CharField(max_length=90)
    rate = models.CharField(max_length=255)
    markup =  models.CharField(max_length=90)
    source =  models.CharField(max_length=90)
    is_enabled =  models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Forex"

class access_tokens(models.Model):
    service_provider =  models.CharField(max_length=90)
    access_token =  models.TextField(max_length=300)
    expires_in =  models.DurationField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Access Tokens"



class zai_payment_details(models.Model):
    zai_user_id =  models.CharField(max_length=90)
    transaction_id = models.CharField(max_length = 150)
    status = models.CharField(max_length= 150, blank=True, null=True)

    class Meta:
           verbose_name_plural = "Zai payment_details"

class zai_agreement_details(models.Model):
    user_id =  models.CharField(max_length=90)
    zai_user_id =  models.CharField(max_length=90)
    zai_email = models.EmailField(max_length=200)
    payid = models.CharField(max_length = 300, null=True, blank=True)
    payid_type = models.CharField(max_length = 300, null=True, blank=True)
    agreement_start_date = models.CharField(max_length = 150)
    agreement_end_date = models.CharField(max_length = 150, null=True, blank=True)
    wallet_account_id = models.CharField(max_length = 150, null=True, blank=True)
    agreement_id = models.CharField(max_length = 250, null=True, blank=True)
    agreement_uuid = models.CharField(max_length = 250, null=True, blank=True)
    bsb_code = models.CharField(max_length = 150, null=True, blank=True)
    account_number = models.CharField(max_length = 150, null=True, blank=True)
    max_amount = models.CharField(max_length = 150)
    auto_renewal = models.BooleanField(default=True)
    status = models.CharField(max_length = 150, null=True, blank=True)

    class Meta:
           verbose_name_plural = "Zai agreement"

class zai_payid_details(models.Model):
    user_id =  models.CharField(max_length=90)
    zai_user_id =  models.CharField(max_length=90)
    zai_email = models.EmailField(max_length=200)
    payid = models.CharField(max_length = 300)
    wallet_account_id = models.CharField(max_length = 150)
    bsb_code = models.CharField(max_length = 150)
    account_number = models.CharField(max_length = 150)
    transaction_id = models.CharField(max_length = 150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
           verbose_name_plural = "Zai payid"


class errors_log(models.Model):
    type =  models.CharField(max_length=250, null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    method = models.CharField(max_length = 150, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
           verbose_name_plural = "Errors Log"

class payment_status_details(models.Model):
    transaction_id = models.CharField(max_length=90)
    status = models.CharField(max_length=90)
    status_reason = models.CharField(max_length=90)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
           verbose_name_plural = "Payment Status Details"


class withdraw_zai_funds(models.Model):
    type = models.CharField(max_length=300, null=True, blank=True)
    transaction_type = models.CharField(max_length=300, null=True, blank=True)
    bank_bic_code = models.CharField(max_length=300, null=True, blank=True)
    transferor = models.CharField(max_length=300, null=True, blank=True)
    creditor_agent_instruction = models.CharField(max_length=300, null=True, blank=True)
    transaction_id = models.CharField(max_length=300, null=True, blank=True)
    source_id = models.CharField(max_length=300, null=True, blank=True)
    receiver_id = models.CharField(max_length=300, null=True, blank=True)
    destination_id = models.CharField(max_length=300, null=True, blank=True)
    wallet_id = models.CharField(max_length=300, null=True, blank=True)
    amount = models.CharField(max_length=300, null=True, blank=True)
    wallet_balance = models.CharField(max_length=300, null=True, blank=True)
    status =  models.CharField(max_length=300, null=True, blank=True)
    reference_id =  models.CharField(max_length=300, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
           verbose_name_plural = "Withdraw Zai Funds Detail"



from django.conf import settings

ref = settings.REFERRALS
TYPE = [(value, value) for key, value in ref.items()]

class referral_type(models.Model):
    type = models.CharField(choices = TYPE, max_length=300, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
           verbose_name_plural = "Referral Types"

class referral(models.Model):
    referral_type = models.ForeignKey(referral_type, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, null=True, blank=True)
    description =  models.CharField(max_length=300, null=True, blank=True)   
    status =  models.CharField(max_length=300, null=True, blank=True)   
    start_date =  models.CharField(max_length=300, null=True, blank=True)   
    end_date =  models.CharField(max_length=300, null=True, blank=True)   
    referred_by_amount = models.CharField(max_length=300, null=True, blank=True)
    referred_to_amount =  models.CharField(max_length=300, null=True, blank=True)  
    currency =  models.CharField(max_length=300, null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
           verbose_name_plural = "Referrals"

class referral_meta(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    referral = models.ForeignKey(referral, on_delete=models.CASCADE)
    referred_by = models.CharField(max_length=300, null=True, blank=True)
    referred_to =  models.CharField(max_length=300, null=True, blank=True)
    transaction_id =  models.CharField(max_length=300, null=True, blank=True)   
    discount =  models.CharField(max_length=300, null=True, blank=True)   
    claimed_date = models.DateField(null=True, blank=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    claimed =  models.BooleanField(default=False)

    class Meta:
           verbose_name_plural = "Referral Meta"

class zai_admin_users(models.Model):
    zai_user_id = models.CharField(max_length=300, null=True, blank=True)
    zai_email = models.CharField(max_length=300, null=True, blank=True)
    wallet_id =  models.CharField(max_length=300, null=True, blank=True)
    bank_name =  models.CharField(max_length=300, null=True, blank=True)
    bank_id =  models.CharField(max_length=300, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
           verbose_name_plural = "Zai RemitAssure Users"
           
class zai_payout_users(models.Model):
    type = models.CharField(max_length=300, null=True, blank=True)   
    zai_user_id = models.CharField(max_length=300, null=True, blank=True)
    zai_email = models.CharField(max_length=300, null=True, blank=True)
    nick_name = models.CharField(max_length=300, null=True, blank=True)
    first_name = models.CharField(max_length=300, null=True, blank=True)
    last_name = models.CharField(max_length=300, null=True, blank=True)
    bank_name =  models.CharField(max_length=300, null=True, blank=True)
    account_name =  models.CharField(max_length=300, null=True, blank=True)   
    account_number =  models.CharField(max_length=300, null=True, blank=True)   
    routing_number = models.CharField(max_length=300, null=True, blank=True)   
    wallet_id =  models.CharField(max_length=300, null=True, blank=True)
    bank_id =  models.CharField(max_length=300, null=True, blank=True)
    account_type =  models.CharField(max_length=300, null=True, blank=True)
    holder_type =  models.CharField(max_length=300, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
           verbose_name_plural = "Zai Payout Accounts"

class austrac_reports(models.Model):
    batch_no = models.CharField(max_length=350, null=True, blank=True)
    reference_no = models.CharField(max_length=350, null=True, blank=True)
    filename = models.CharField(max_length=350, null=True, blank=True)
    type = models.CharField(max_length=350, null=True, blank=True)
    transactions_count = models.IntegerField(null=True, blank=True, default=0)
    file = models.FileField(upload_to='austrac/', blank=True, null=True)
    path = models.CharField(max_length=350, null=True, blank=True)
    status = models.CharField(max_length=350, null=True, blank=True, default='pending')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
           verbose_name_plural = "Austrac Reports"

    def save(self, *args, **kwargs):
        if self.file and not self.path:
            self.path = settings.BASE_URL+self.file.url
            super(austrac_reports, self).save(*args, **kwargs)

class austrac_reports_detail(models.Model):
    austrac_reports_id = models.ForeignKey(austrac_reports, on_delete=models.CASCADE)
    reference_no = models.CharField(max_length=350, null=True, blank=True)
    transaction_id = models.CharField(max_length=350, null=True, blank=True)
    type = models.CharField(max_length=350, null=True, blank=True)
    status = models.CharField(max_length=350, null=True, blank=True, default='pending')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Austrac Reports Detail"
