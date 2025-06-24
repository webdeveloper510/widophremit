from rest_framework import serializers
from payment_app.models import *


class Recipient_List_Serializer(serializers.ModelSerializer):
    class Meta:
        model= Recipient
        fields=['id','first_name','middle_name','last_name','email','mobile','flat','building',
                    'street', 'city','state','country', 'postcode','update_profile','transfer_now']
        
class Recipient_bank_detail_Serializer(serializers.ModelSerializer):
    class Meta:
        model= Recipient_bank_details
        fields=['id','bank_name','swift_code', 'bank_address','account_number','recipient_id']

        extra_kwargs={
            'bank_name': {'error_messages': {'required': "bank_name is required",'blank':'please provide a bank name'}},
            'account_name': {'error_messages': {'required': "account_name is required",'blank':'account name could not blank'}},
          }

class User_Profile_Serializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id', 'customer_id', 'mobile_verified', 'email','First_name','Middle_name','Last_name','Date_of_birth','referral_code','referred_by','Gender','Country_of_birth','mobile','location','is_verified','is_digital_Id_verified','stripe_customer_id', 'occupation','payment_per_annum','value_per_annum']        

# from rest_framework import serializers

class SearchModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction_details
        fields = '__all__'

class Transaction_details_web_Serializer(serializers.ModelSerializer):
    class Meta:
        model= Transaction_details
        fields=['id', 'recipient','exchange_rate', 'date', 'tm_label','transaction_id','card_type','recipient_name','customer_id','recipient','send_currency','receive_currency','amount','send_method', 'receive_amount','receive_method', 'payment_status', 'payment_status_reason','tm_status','reason','created_at', 'risk_score','risk_group']

