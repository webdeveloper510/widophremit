from rest_framework import serializers
from .models import *

class RecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model= Recipient
        fields=['id','first_name','last_name','mobile','country_code','country','update_profile','transfer_now']

    
class Recipient_list_Serializer(serializers.ModelSerializer):
    class Meta:
        model= Recipient
        fields=['id','first_name','middle_name','last_name','email','mobile','flat','building',
                    'street', 'city','state','country', 'country_code', 'postcode','update_profile','transfer_now','address']

class Recipient_bank_details_Serializer(serializers.ModelSerializer):
    class Meta:
        model= Recipient_bank_details
        fields=['bank_name','account_name', 'account_number','recipient_id']

        extra_kwargs={
            'bank_name': {'error_messages': {'required': "bank_name is required",'blank':'please provide a bank name'}},
            'account_name': {'error_messages': {'required': "account_name is required",'blank':'account name could not blank'}},
          }

class Transaction_details_web_Serializer(serializers.ModelSerializer):
    class Meta:
        model= Transaction_details
        fields=['id', 'updated_at', 'rule','aml_pep_status','recipient_name','total_amount','discount_amount','recipient','exchange_rate', 'date', 'tm_label','transaction_id','card_type','recipient_name','customer_id','recipient','send_currency','receive_currency','amount','send_method', 'receive_amount','receive_method', 'payout_partner','payment_status', 'payment_status_reason','tm_status','reason','created_at', 'risk_score','risk_group']


class stripe_create_card_details_Serializer(serializers.ModelSerializer):
    class Meta:
        model= stripe_card_details
        fields=['id','name','card_number','expiry_month','expiry_year']


class stripe_card_details_Serializer(serializers.ModelSerializer):
    class Meta:
        model= stripe_card_details
        fields=['id','name','card_number','expiry_month','expiry_year','card_token','card_id']


class Email_template_images_Serializer(serializers.ModelSerializer):
    class Meta:
        model= Email_template_images
        fields=['id','image']

class Transaction_history_Serializer(serializers.ModelSerializer):
    class Meta:
        model= Transaction_details
        fields=['id','customer_id', 'tm_label','receive_amount','card_type','recipient','recipient_name','send_currency','receive_currency','amount','send_method','receive_method','payout_partner','payment_status', 'payment_status_reason','tm_status', 'reason','transaction_id','date']

class Transaction_status_Serializer(serializers.ModelSerializer):
    class Meta:
        model= Transaction_details
        fields=['recipient_name','receive_amount','receive_currency', 'reason','payment_status', 'payment_status_reason','tm_status','date']

class Forex_Serializer(serializers.ModelSerializer):
    class Meta:
        model= forex
        fields=['id','source_currency','destination_currency', 'markup','source', 'is_enabled']

class Update_Recipient_Serializer(serializers.ModelSerializer):
    class Meta:
        model= Recipient
        fields=['id','first_name','middle_name','last_name','email','mobile','flat','building','street', 'city','state','country', 'country_code', 'postcode','update_profile','transfer_now','address']

class Update_Recipient_Bank_Serializer(serializers.ModelSerializer):
    class Meta:
        model= Recipient_bank_details
        fields=['bank_name','account_name', 'account_number','recipient_id']