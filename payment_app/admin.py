from django.contrib import admin
from . models import *

@admin.register(Transaction_details)
class Transaction_detailsModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'paid_amount','aml_pep_status' ,'rule','agreement_id', 'total_amount','discount_amount', 'exchange_rate', 'tm_label', 'customer_id','receive_amount','recipient','recipient_name','send_currency','receive_currency','amount','send_method','receive_method','payout_partner','payment_status', 'payment_status_reason','tm_status', 'reason','transaction_id','card_token', 'risk_score','risk_group','payment_gateway_transaction_id')

@admin.register(Recipient)
class RecipientModelAdmin(admin.ModelAdmin):
    list_display = ('id','user','first_name','middle_name','last_name','email','mobile','flat','building',
                    'street', 'postcode','city','state','country_code','country','update_profile','transfer_now')

@admin.register(Recipient_bank_details)
class Recipient_bank_detailsModelAdmin(admin.ModelAdmin):
    list_display = ('id','recipient','bank_name','account_name', 'account_number')

@admin.register(stripe_card_details)
class card_detailsModelAdmin(admin.ModelAdmin):
    list_display = ('id','customer_id','name','card_number','expiry_month','expiry_year','card_token','card_id')

@admin.register(stripe_card_token)
class card_detailsModelAdmin(admin.ModelAdmin):
    list_display = ('id','customer_id','name','card_token', 'card_id')

@admin.register(send_currency_list)
class send_currency_listModelAdmin(admin.ModelAdmin):
    list_display = ('id','currency','country')

@admin.register(receive_currency_list)
class receive_currency_listModelAdmin(admin.ModelAdmin):
    list_display = ('id','currency','country')

@admin.register(forex)
class Forex_ModelAdmin(admin.ModelAdmin):
    list_display = ('id','source_currency','rate','destination_currency','markup','source', 'is_enabled')

@admin.register(access_tokens)
class access_tokensModelAdmin(admin.ModelAdmin):
    list_display = ('id','service_provider','access_token','expires_in','created_at','updated_at')

admin.site.register(zai_payment_details)
admin.site.register(zai_agreement_details)
admin.site.register(zai_payid_details)
admin.site.register(payment_status_details)
admin.site.register(withdraw_zai_funds)

admin.site.register(referral_type)
admin.site.register(referral)
admin.site.register(referral_meta)

# admin.site.register(errors_log)