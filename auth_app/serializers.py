from tokenize import TokenError
from auth_app.utils import Util
from wsgiref.validate import validator
from rest_framework import serializers
from auth_app.models import User
from django.utils.encoding import smart_str,force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from Widoph_Remit.settings import BASE_URL
import datetime 
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from .models import *
from django.core.mail import EmailMultiAlternatives, message
import smtplib
from email.message import EmailMessage
from django.conf import settings
import random
from Widoph_Remit.package import *
from django.utils import timezone
import re

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','email','password','location','mobile','country_code','payment_per_annum','value_per_annum']

        extra_kwargs={
            'email': {'error_messages': {'required': "Please enter email",'blank':'Please enter email'}},
            'password': {'error_messages': {'required': "Please enter password",'blank':'Please enter password'}},
            'location': {'error_messages': {'required': "Please select country",'blank':'Please select country'}},
            'mobile': {'error_messages': {'required': "Please enter mobile",'blank':'Please enter mobile'}},
            'country_code': {'error_messages': {'required': "Please enter country iso code",'blank':'Please enter country iso code'}},
          }

    def create(self, validated_data,):
        return User.objects.create(
            email=validated_data['email'],
            country_code = validated_data['country_code'],
            location=validated_data['location'],
            mobile=validated_data['mobile'],
            password = make_password(validated_data['password']),
            payment_per_annum = 'Tier-1 Less than 5 times',
            value_per_annum = 'Tier-1 Less than $30,000'
)

class VerifyEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['email','email_otp']

        extra_kwargs={
            'email': {'error_messages': {'required': "Please enter email",'blank':'Please enter email'}},
            'password': {'error_messages': {'required': "Please enter password",'blank':'Please enter password'}},
            'location': {'error_messages': {'required': "Please select country",'blank':'Please select country'}},
            'mobile': {'error_messages': {'required': "Please enter mobile",'blank':'Please enter mobile'}},
          }

         
class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=250)
    class Meta:
        model=User
        fields=['email','password']
        extra_kwargs={
        'email': {'error_messages': {'required': "email is required",'blank':'please provide a email'}},
        'password': {'error_messages': {'required': "password is required",'blank':'please enter a email'}}     
    }

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id', 'customer_id', 'mobile_verified', 'email','First_name','Middle_name','Last_name','Date_of_birth','referred_by','Gender','Country_of_birth','mobile','location','is_verified','is_digital_Id_verified','aml_pep_status','stripe_customer_id', 'occupation','payment_per_annum','value_per_annum', 'created_at','destination_currency','documents']        

class User_Update_Profile_Serializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','First_name','Last_name','email','mobile','Gender','Country_of_birth','location', 'occupation']        

class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class User_list_Serializer(serializers.ModelSerializer):
    class Meta:
        model= User
        fields=['id','customer_id', 'country_code','email','First_name','Middle_name','Last_name','Date_of_birth','Gender','Country_of_birth','mobile','location','is_verified','occupation','payment_per_annum','value_per_annum','aml_pep_status','created_at','is_digital_Id_verified']        

class User_address_Serializer(serializers.ModelSerializer):
    class Meta:
        model= User_address
        fields=['id','building','street', 'postcode','city','state','country','country_code','address']        

class User_address_list_Serializer(serializers.ModelSerializer):
    class Meta:
        model= User_address
        fields=['flat','building','street', 'postcode','city','state','country','country_code','address']        

