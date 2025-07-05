from pathlib import Path
from datetime import timedelta
import smtplib
from django.utils import timezone
import datetime
from datetime import date
from dotenv import load_dotenv
import os
from Widoph_Remit.settings import *

load_dotenv() 

# HOST = "TEST"
# HOST = "DEV"
HOST= "DEV"
# HOST= "LOCAL"

if HOST == "TEST":
  SEND_OTP = False
  SEND_EMAIL = True
if HOST == "LIVE":
  SEND_OTP = True
  SEND_EMAIL = True
else:
  SEND_OTP = False
  SEND_EMAIL = False

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-3i7eb85@4c(4r9rc7+5y69qsza11b22!ochy#!pl9t#017v74n'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

if HOST == "LIVE":
  ALLOWED_HOSTS = ['api.widophremit.com','widophremit.com']
elif HOST == "TEST":
  ALLOWED_HOSTS = ['admin.qa.widophremit.com','qa.widophremit.com']
elif HOST == "DEV":
  ALLOWED_HOSTS = ['54.151.50.98','54.151.50.98:8000',]
else:
  INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
  ]
  DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: True,
  }
  ALLOWED_HOSTS = ['*']

#
# Application definition

INSTALLED_APPS = [
  'django.contrib.admin',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.messages',
  'django.contrib.staticfiles',
  'corsheaders',
  'rest_framework',
  'rest_framework_simplejwt',
  'rest_framework.authtoken',
  'widget_tweaks',
  'auth_app',
  'payment_app',
  'users',
  'mophy',
  'service_providers',
  'mobile_app',
  'mobile_payment_app',
  'monoova',
  # "debug_toolbar",
  
]

REST_FRAMEWORK = {
  'DEFAULT_AUTHENTICATION_CLASSES': [
      'rest_framework.authentication.BasicAuthentication',
      'rest_framework.authentication.TokenAuthentication',
      'rest_framework.authentication.SessionAuthentication', 
],

  'DEFAULT_PERMISSION_CLASSES': [
     'rest_framework.permissions.IsAuthenticated',
     'rest_framework.permissions.IsAdminUser',
     ]
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
  )
}

MIDDLEWARE = [
  'django.middleware.security.SecurityMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'whitenoise.middleware.WhiteNoiseMiddleware',
  'corsheaders.middleware.CorsMiddleware',
  'django.middleware.common.CommonMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.middleware.clickjacking.XFrameOptionsMiddleware'
  # 'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'Widoph_Remit.urls'

TEMPLATES = [
  {
      'BACKEND': 'django.template.backends.django.DjangoTemplates',
      'DIRS': ['templates'],
      'APP_DIRS': True,
      'OPTIONS': {
          'context_processors': [
              'django.template.context_processors.debug',
              'django.template.context_processors.request',
              'django.contrib.auth.context_processors.auth',
              'django.contrib.messages.context_processors.messages',
              'custom_context_processor.dz_static'
          ],
      },
  },
]

WSGI_APPLICATION = 'Widoph_Remit.wsgi.application'



# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if HOST == "LOCAL":
  DATABASES = {
    'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'WidophRemitLocal',
    'USER': 'root',
    # 'PASSWORD': '1234',
    'PASSWORD': '',
    'HOST': 'localhost', # Or an IP Address that your DB is hosted on
    'PORT': '3306',
    # 'OPTIONS': {
    #         'read_default_file': '/opt/lampp/etc/my.cnf',
    #     }
    }
  }
elif HOST == 'LIVE':
  DATABASES = {
  'default': {
  'ENGINE': 'django.db.backends.mysql',
  'NAME': 'WidophRemit',
  'USER': os.environ.get('DB_USER'),
  'PASSWORD': os.environ.get('DB_PASSWORD'),
  'HOST': 'localhost', # Or an IP Address that your DB is hosted on
  'PORT': '3306',
  'OPTIONS': {
          'read_default_file': '/opt/lampp/etc/my.cnf',
      }
  }
}
elif HOST == 'DEV':
  DATABASES = {
  'default': {
  'ENGINE': 'django.db.backends.mysql',
  'NAME': 'WidophRemitDev',
  'USER': os.environ.get('DB_USER_DEV'),
  'PASSWORD': os.environ.get('DB_PASSWORD_DEV'),
  'HOST': 'localhost', # Or an IP Address that your DB is hosted on
  'PORT': '3306',
  'OPTIONS': {
          'read_default_file': '/opt/lampp/etc/my.cnf',
      }
  }
}
else:
  DATABASES = {
  'default': {
  'ENGINE': 'django.db.backends.mysql',
  'NAME': 'WidophRemitTest',
  'USER': os.environ.get('DB_USER_QA'),
  'PASSWORD': os.environ.get('DB_PASSWORD_QA'),
  'HOST': 'localhost', # Or an IP Address that your DB is hosted on
  'PORT': '3306',
  'OPTIONS': {
          'read_default_file': '/opt/lampp/etc/my.cnf',
      }
  }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
  {
      'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
  },
  {
      'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
  },
  {
      'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
  },
  {
      'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
  },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'Asia/Calcutta'
TIME_ZONE = 'Australia/Victoria'

USE_I18N = True

USE_L10N = False

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "static/"
if DEBUG:
  STATICFILES_DIRS = [BASE_DIR / "static"]
else:
  STATIC_ROOT = STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = '/media/'
MEDIA_ROOT = Path(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

if HOST == "LOCAL":
  SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
  }
else:
  #JWT settings
  SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
  }

if HOST == "LOCAL":
  CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:3000",
  ]

  BASE_URL= "http://127.0.0.1:8000"
  FRAUDNET_ORDER = "L"
  EMAIL_ACTIVATION_LINK = "http://localhost:3000/remi-user-email-verification/"
  PAYMENT_ID = str("L")+str(date.today())
  
elif HOST == "DEV":
  CORS_ALLOWED_ORIGINS = [
  "http://54.151.50.98:8000",
  "http://54.151.50.98:8001",
  "http://54.151.50.98",
  "http://localhost:3000",
  "http://localhost:5173",
  ]
  
  BASE_URL= "http://54.151.50.98:8000"
  FRAUDNET_ORDER = "DEV"
  EMAIL_ACTIVATION_LINK = "http://54.151.50.98/remi-user-email-verification/"
  PAYMENT_ID = str("D")+str(date.today())

elif HOST == "LIVE":
  CORS_ALLOWED_ORIGINS = [
  "https://api.widophremit.com",
  "https://widophremit.com",
  "http://localhost:3000",
  ]
  CSRF_TRUSTED_ORIGINS = ['https://api.widophremit.com']
  BASE_URL= "https://api.widophremit.com"
  FRAUDNET_ORDER = "LIVE"
  EMAIL_ACTIVATION_LINK = "https://widophremit.com/remi-user-email-verification/"
  PAYMENT_ID = str(date.today())

else:
  CORS_ALLOWED_ORIGINS = [
  "http://localhost:3000",
  "https://qa.widophremit.com",
  "https://admin.qa.widophremit.com",
  ]

  CSRF_TRUSTED_ORIGINS = ['https://admin.qa.widophremit.com']
  BASE_URL= "https://admin.qa.widophremit.com"
  FRAUDNET_ORDER = "TEST"
  EMAIL_ACTIVATION_LINK = "https://qa.widophremit.com/remi-user-email-verification/"
  PAYMENT_ID = str(date.today())


#exchange rate API key
EXCHANGE_RATE_API_KEY = os.environ.get('EXCHANGE_RATE_API_KEY')
# API_KEY = "10DElRZfhipXcUoRxcRC0yONpDlhpht0"

#stripe
if HOST == "LIVE":
  #test keys
  API_PUBLISH_KEY = os.environ.get('STRIPE_API_PUBLISH_KEY_LIVE')
  API_SECRET_KEY = os.environ.get('STRIPE_API_SECRET_KEY_LIVE')
  STRIPE_URL = os.environ.get('STRIPE_URL')
else:
  API_PUBLISH_KEY = os.environ.get('STRIPE_API_PUBLISH_KEY')
  API_SECRET_KEY = os.environ.get('STRIPE_API_SECRET_KEY')
  STRIPE_URL = os.environ.get('STRIPE_URL')
 

# Cloud Currency details

if HOST=="LIVE":
  LOGIN_ID =   os.environ.get('LOGIN_ID_LIVE')
  CC_API_KEY = os.environ.get('CC_API_KEY_LIVE')
else:
  LOGIN_ID = os.environ.get('LOGIN_ID')
  CC_API_KEY = "00a95ad3481ee0a42b0dd3fea685a78be478583b1c607902b11529b76094a972"
CC_URL = "https://devapi.currencycloud.com/v2"

#DIGITAL ID
if HOST == "LIVE":
  DIGITAL_ID_TOKEN = os.environ.get('DIGITAL_ID_TOKEN_LIVE')
  DIGITAL_ID_URL = "https://api.digitalid.com"
  DIGITAL_CLIENT_ID = os.environ.get('DIGITAL_CLIENT_ID_LIVE')
  DIGITAL_CLIENT_SECRET = os.environ.get('DIGITAL_CLIENT_SECRET_LIVE')
  DIGITAL_ID_REDIRECT_URL = "https://digitalid.com/oauth2/echo"
else:
  DIGITAL_ID_TOKEN = os.environ.get('DIGITAL_ID_TOKEN')
  DIGITAL_ID_URL = "https://api.digitalid-sandbox.com"
  DIGITAL_CLIENT_ID = os.environ.get('DIGITAL_CLIENT_ID')
  DIGITAL_CLIENT_SECRET = os.environ.get('DIGITAL_CLIENT_SECRET')
  DIGITAL_ID_REDIRECT_URL = "https://digitalid-sandbox.com/oauth2/echo"
  
if HOST == "LIVE":
  EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
  EMAIL_HOST = "australia1.rebel.com"
  EMAIL_PORT = 587 #465 for SSL#
  EMAIL_USE_TLS = True
  EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER_LIVE')
  EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD_LIVE')
else:
  EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
  EMAIL_HOST = "australia1.rebel.com"
  EMAIL_PORT = 587 #465
  EMAIL_USE_TLS = True
  EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
  EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

EMAIL_VERIFICATION_TOKEN_EXPIRED = datetime.timedelta(days=3)
RESET_PASSWORD_TOKEN_EXPIRED = timedelta(minutes=15)
MOBILE_VERIFICATION_TOKEN_EXPIRED = datetime.timedelta(minutes=15)
EMAIL_ACTIVATION_LINK_EXPIRED = datetime.timedelta(days=7)

# Fraud.net
if HOST == "LIVE":
  SANDBOX_URL =  os.environ.get('SANDBOX_URL_LIVE')
  FRAUD_TOKEN = os.environ.get('FRAUD_TOKEN_LIVE')
  FRAUDNET_APPLICATION_TOKEN = os.environ.get('FRAUDNET_APPLICATION_TOKEN_LIVE')
  FRAUDNET_APPLICATION_URL = os.environ.get('FRAUDNET_APPLICATION_URL_LIVE')
  WEBHOOK_TOKEN = os.environ.get('WEBHOOK_TOKEN')
else:
  SANDBOX_URL =  os.environ.get('SANDBOX_URL')
  FRAUD_TOKEN = os.environ.get('FRAUD_TOKEN')
  FRAUDNET_APPLICATION_TOKEN = os.environ.get('FRAUDNET_APPLICATION_TOKEN')
  FRAUDNET_APPLICATION_URL = os.environ.get('FRAUDNET_APPLICATION_URL')
  WEBHOOK_TOKEN = os.environ.get('WEBHOOK_TOKEN')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'auth_app.User'

BAD_REQUEST = "400"
SUCCESS_CODE = "200"
BAD_REQUEST_MESSAGE = "Bad request"
SUCCESS_MESSAGE = "Success"

#bulk sms
SMS_TOKEN = os.environ.get('SMS_TOKEN')
SENDER_ID = os.environ.get('SENDER_ID')

#Firebase server token
FIREBASE_SERVERTOKEN  = os.environ.get('FIREBASE_SERVERTOKEN')

#TWilio
TWILIO_SID = os.environ.get('TWILIO_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_SENDER_ID = os.environ.get('TWILIO_SENDER_ID')
TWILIO_URL = os.environ.get('TWILIO_URL')
TWILIO_ACCESS_TOKEN = os.environ.get('TWILIO_ACCESS_TOKEN')

#Veriff Credentials
if HOST == "LIVE":
  VERIFF_API_KEY = os.environ.get('VERIFF_API_KEY_LIVE')
  VERIFF_SECRET_KEY = os.environ.get('VERIFF_SECRET_KEY_LIVE')
  VERIFF_URL = "https://stationapi.veriff.com"
else:
  VERIFF_API_KEY = os.environ.get('VERIFF_API_KEY')
  VERIFF_SECRET_KEY = os.environ.get('VERIFF_SECRET_KEY')
  VERIFF_URL= "https://stationapi.veriff.com"

#ZAI credentials
if HOST == "LIVE":
  #live zai
  ZAI_TOKEN_URL = os.environ.get('ZAI_TOKEN_URL_LIVE')
  ZAI_URL = os.environ.get('ZAI_URL_LIVE')
  ZAI_GRANT_TYPE = "client_credentials"
  ZAI_CLIENT_ID = os.environ.get('LIVE_ZAI_CLIENT_ID')
  ZAI_CLIENT_SECRET = os.environ.get('LIVE_ZAI_CLIENT_SECRET')
  ZAI_SCOPE = os.environ.get('LIVE_ZAI_SCOPE')
  ZAI_TOKEN_EXPIRES_IN =  timedelta(minutes=50)
  ZAI_REMIT_USER_ID = os.environ.get('LIVE_ZAI_REMIT_USER_ID')
  ZAI_URL_ACCOUNT = os.environ.get('ZAI_URL_ACCOUNT_LIVE')
  ZAI_NPP_URL = "https://int-npp-master.platforms.prelive.assemblypayments.com/npp/receive-request"
  ZAI_PAYID_DOMAIN = "@remitassure.com"
  ABN_NO = os.environ.get('LIVE_ZAI_ABN_NO')
else:
  ZAI_TOKEN_URL = "https://au-0000.sandbox.auth.assemblypay.com"
  ZAI_URL = "https://test.api.promisepay.com"
  ZAI_GRANT_TYPE = "client_credentials"
  ZAI_CLIENT_ID = os.environ.get('ZAI_CLIENT_ID')
  ZAI_CLIENT_SECRET = os.environ.get('ZAI_CLIENT_SECRET')
  ZAI_SCOPE = "im-au-06/f05b53c0-dda1-013b-880e-0a58a9feac03:04a309ce-d8a0-4558-8470-7b7e89e0ba45:3"
  ZAI_TOKEN_EXPIRES_IN =  timedelta(minutes=50)
  ZAI_REMIT_USER_ID = os.environ.get('ZAI_REMIT_USER_ID')
  ZAI_URL_ACCOUNT = "https://sandbox.au-0000.api.assemblypay.com"
  ZAI_NPP_URL = "https://int-npp-master.platforms.prelive.assemblypayments.com/npp/receive-request"
  ZAI_PAYID_DOMAIN = "@mywidophremit.com"
  ABN_NO = os.environ.get('ZAI_ABN_NO')


#Veriff session url
VERIFF_SESSION_URL = "https://stationapi.veriff.com/v1/sessions"
#NOTIFICATIONS MESSAGES
NOTIFICATION_USER_MSG = "New user has signed up with "
NOTIFICATION_TRANSACTION_MSG = "New transaction created for "


#send notifications to remitassure
if HOST == "LIVE":
  REMIT_ASSURE_MOBILE = os.environ.get('REMIT_ASSURE_NOTIFICATION_MOBILE_LIVE')
  REMIT_ASSURE_EMAIL = os.environ.get('REMIT_ASSURE_NOTIFICATION_EMAIL_LIVE')
  INVITE_LINK = "https://widophremit.com/sign-up"
else:
  REMIT_ASSURE_MOBILE = os.environ.get('REMIT_ASSURE_NOTIFICATION_MOBILE')
  REMIT_ASSURE_EMAIL = os.environ.get('REMIT_ASSURE_NOTIFICATION_EMAIL')
  INVITE_LINK = "https://qa.widophremit.com/sign-up"

SESSION_COOKIE_AGE = 1800  # 30 minutes in seconds
SESSION_SAVE_EVERY_REQUEST = True

# transaction status

TRANSACTION = {
  'incomplete':"Incomplete",
  'pending_payment':"Pending Payment",
  'pending_review':"Pending Review and Processing",
  'cancelled': "Cancelled", #not included in payment views
  'completed':"Processed"  #not included in payment views
}

SEND_CURRENCY_LIST = [{'currency': 'AUD', 'country': 'Australia'}, {'currency': 'NZD', 'country': 'New Zealand'}]
RECEIVE_CURRENCY_LIST = [{'currency': 'PHP', 'country': 'Philippines'}, {'currency': 'GHS', 'country': 'Ghana'}, {'currency': 'THB', 'country': 'Thailand'}, {'currency': 'VND', 'country': 'Vietnam'}, {'currency': 'KES', 'country': 'Kenya'}, {'currency': 'USD', 'country': 'Nigeria'}, {'currency': 'NGN', 'country': 'Nigeria'}]

#Welcome email template links
if HOST == "LIVE":
  SUPPORT_CENTER_LINK = "https://widophremit.com/help"
  HOME_LINK = "https://widophremit.com/"
  UNSUBSCRIBE_LINK = "https://widophremit.com/"
  WIDOPH_REMIT_LINK = "https://widophremit.com/"
  LOGIN_LINK = "https://widophremit.com/login"
else:
  SUPPORT_CENTER_LINK = "https://qa.widophremit.com/help"
  HOME_LINK = "https://qa.widophremit.com/"
  UNSUBSCRIBE_LINK = "https://qa.widophremit.com/"
  WIDOPH_REMIT_LINK = "https://qa.widophremit.com/"
  LOGIN_LINK = "https://qa.widophremit.com/login"

#Brevo for newsletters
BREVO_URL = os.environ.get('BREVO_URL')
BREVO_API_KEY = os.environ.get('BREVO_API_KEY')
if HOST == "LIVE":
  LIST_ID = os.environ.get('LIST_ID_LIVE')
else:
  LIST_ID = os.environ.get('LIST_ID')


#admindashboard
PAYIN_CURRENCY = "AUD"
PAYOUT_CURRENCY = "USD"

ZAI = {
  'payid': 'zai_payid_per_user',
  'payto':'zai_payto_agreement',
}

REFERRALS = {
  'invite': 'Invite',
  'birthday':'Birthday',
  'transaction':'Transaction',
  'amount':'Amount',
  'festival':'Festival'
}

REFERRAL_AMOUNT = 1000

USER_COUNTRIES = {
  'Australia': 'AU',
  'New Zealand':'NZ'
}

RECIPIENT_COUNTRIES = {
  'Australia': 'AU',
  'Nigeria':'NGA',
  'Vietnam':'VNM',
  'Philippines':'PHL',
  'Thailand':'THA',
  'Kenya':'KEN',
  'Ghana':'GHA'
}


COUNTRY_CODE = {
  'Australia':'+61',
  'New Zealand':'+64'
}

#permission modules to show to user in adminpanel
PERMISSION_MODULES = ['Admin User','Role', 'Customer','Recipient','Transaction','Veriff','Transaction Monitoring','Forex','Activity Report','Zai','Corridor','Loyality Program']

#WidophRemit zai users to receive funds
if HOST == 'LIVE':
  ZAI_ADMIN_USERS = [
    {'bank_name':"ANZ Bank",'zai_user_id':"",'zai_email':""},
    {'bank_name':"Commbank",'zai_user_id':"",'zai_email':""}
  ]
else:
  ZAI_ADMIN_USERS = [
    {'bank_name':"Bank of Australia (Platform user)",'zai_user_id':"",'zai_email':""},
    {'bank_name':"Bank of Australia",'zai_user_id':"",'zai_email':""}
  ]

#discount amount for invitee and inviter
REFERRED_BY_AMOUNT = 50 #invited by
REFERRED_TO_AMOUNT = 25 #invited to

#custom otp for custom users to login with custom mobiles and emails
CUSTOM_OTP = "902300"
CUSTOM_MOBILES = []
CUSTOM_EMAILS = []

#optional fields for user table
PROFILE_COMPLETED_OPTIONAL_LOWER_FIELDS = ['middle_name','flat','stripe_customer_id','country_of_birth','is_verified','destination_currency', 'referred_by', 'gender','aml_pep_status','address']

#path to download csv file
CSV_DOWNLOAD_PATH = os.getcwd() +"/static/mophy/csvholder"

#Transactions CSV Filters (key is forntend key and value is database field name)
CSV_CUSTOMER_FILTER_KEYS = [
  {'Promo Marketing': "promo_marketing"},
  {'Email': "is_verified"},
  {'KYC Status': "is_digital_Id_verified"},
  {'AML/PEP Status': "aml_pep_status"}
]

#CSV option values to show in html file on customer page (on left side are keys which will be selected by user and on right side DB values of selected key)
CSV_CUSTOMER_FILTER_VALUES = [
  {'promo_marketing': ["Yes", "No"]},
  {'is_verified': ["Verified", "Unverified"]},
  {'is_digital_Id_verified': ["Pending","Approved","Declined"]},
  {'aml_pep_status': ["Pending","Matched","No Matched"]}
]

#Transactions CSV Filters (key is forntend key and value is database field name)
CSV_TRANSACTION_FILTER_KEYS = [
  {'Payin Currency': "send_currency"},
  {'Payout Currency': "receive_currency"},
  {'TM Status': "tm_status"},
  {'Payment Status': "payment_status"},
  {'Payin Method': "send_method"},
  {'AML/PEP Status': "aml_pep_status"}
]

#CSV option values to show in html file on transaction page (on left side are keys which will be selected by user and on right side DB values of selected key)
CSV_TRANSACTION_FILTER_VALUES = [
  {'send_currency': ["AUD", "NZD"]},
  {'receive_currency': ["USD","KES","VND","NGN","PHP","GHS","THB"]},
  {'tm_status': ["Approved","Queued","Cancelled"]},
  {'payment_status': ["Pending Payment","Pending Review and Processing","Cancelled","Processed","Incomplete"]},
  {'send_method': ["PayID","PayTo Agreement"]},
  {'aml_pep_status': ["Pending","Matched","No Matched"]},
]

#CSV original DB values (on left side, values fetched from html files and on right side, database column name)
CSV_DB_VALUES_ = [
  {"True":True},{"False":False},
  {"Yes":True},{"No":False},
  {"Verified":True}, {"Unverified":False},
  {"Pending":"pending"},{"Approved":"approved"},{"Declined":"declined"},
  {"Matched":True},{"No Matched":False},
  {"PayID":"zai_payid_per_user"},{"PayTo Agreement":"zai_payto_agreement"},
]

#fields to show in csv file with filter values (on left side, column names to show in file and on right side, database column name)
USER_CSV_ALL_FIELDS = [
  {'Cust ID': 'customer_id', 
   'Email': 'email', 
   'Mobile': 'mobile', 
   'First Name': 'First_name', 
   'Last Name': 'Last_name',
   'DOB': 'Date_of_birth',
   'Referral Code':'referral_code',
   'Promo Marketing': 'promo_marketing',
   'Email Verification': 'is_verified',
   'KYC Verification': 'is_digital_Id_verified',
   'AML/PEP Status': 'aml_pep_status',
   'Occupation': 'occupation',
   'Payment Per Annum':'payment_per_annum',
   'Value Per Annum': 'value_per_annum',
   'Status': 'delete'}
]

#fields to show in csv file with filter values (on left side, column names to show in file and on right side, database column name)
TRANSACTION_CSV_ALL_FIELDS = [
  {
   'Transaction ID': 'transaction_id', 
   'Date': 'date',
   'Cust ID': 'customer_id', 
   'Beneficiary Name': 'recipient_name', 
   'Payin Amount': 'amount', 
   'Payout Amount': 'receive_amount', 
   'Payin Method': 'send_method',
   'Payout Method': 'receive_method',
   'Payout Partner': 'payout_partner',
   'FX':'exchange_rate',
   'Payment Status': 'payment_status',
   'AML/PEP Status': 'aml_pep_status',
   'TM Status': 'tm_status',
   'TM Rule ': 'rule',
   'Risk Score': 'risk_score',
   'Risk Group': 'risk_group',
   }
]

#Custom values of column fields to show in CSV file
CSV_FILE_FIELD_VALUES_ = [
  {'promo_marketing': [{True:"Opted", False:"Not Opted"}]},
  {'delete': [{True:"Disabled", False:"Enabled"}]},
  {'aml_pep_status': [{True: "False", False:"True"}]},
  {'is_verified': [{True: "Completed", False: "Pending"}]},
  {'send_method': [{'zai_payid_per_user': "Zai PayID", 'zai_payto_agreement': "Zai PayTo Agreement"}]}
]


#referral types
REFERRAL_TYPES = ['Invite','Birthday']


#Transaction usage values 
PAYMENT_PER_ANNUM_LIST = []

VALUE_PER_ANNUM_LIST = []

#update list for adminpanel for Tiers
ADMIN_PAYMENT_PER_ANNUM_LIST = []

ADMIN_VALUE_PER_ANNUM_LIST = []

ADMIN_VERIFF_STATUS_LIST = [
  {'Yes': "approved"},
  {'No': "declined" },
  {'Pending': "pending"},
  {'Suspended': "resubmission_requested"}
]

ADMIN_DOCUMENTS_STATUS_LIST = [
  {'Approved': "approved"},
  {'Failed': "failed" }
  # {'Pending': "pending"}
]

#ZAI PAYOUT RECEIVER ACCOUNTS
if HOST == 'LIVE':
  ZAI_PAYOUT_USERS = [
    
  ]
else:
  ZAI_PAYOUT_USERS = [
    {'bank_name':"Bank of Australia",'zai_user_id':"",'zai_email':""},
    {'bank_name':"Bank of Australia",'zai_user_id':"",'zai_email':""}
  ]


#AUSTRAC
if HOST == "LIVE":
  AUSTRAC_USER_ID = os.environ.get('AUSTRAC_USER_ID_LIVE')
  AUSTRAC_PASSWORD = os.environ.get('AUSTRAC_PASSWORD_LIVE')
  AUSTRAC_RE_NUMBER = os.environ.get('AUSTRAC_RE_NUMBER_LIVE')
  XML_RE_NUMBER = os.environ.get('XML_RE_NUMBER_LIVE')
  AUSTRAC_VERSION = os.environ.get('AUSTRAC_VERSION_LIVE')
  AUSTRAC_IFTI_URL = "https://online.austrac.gov.au/ao-trn/automatedFileUpload"
  AUSTRAC_TTR_URL = "https://online.austrac.gov.au/ao-trn/automatedFileUpload"
else:
  AUSTRAC_USER_ID = os.environ.get('AUSTRAC_USER_ID')
  AUSTRAC_PASSWORD = os.environ.get('AUSTRAC_PASSWORD')
  XML_RE_NUMBER = os.environ.get('XML_RE_NUMBER')
  AUSTRAC_RE_NUMBER = os.environ.get('AUSTRAC_RE_NUMBER')
  AUSTRAC_VERSION = os.environ.get('AUSTRAC_VERSION')
  AUSTRAC_IFTI_URL = "https://online.austrac.gov.au/ao-trn/automatedFileUpload"
  AUSTRAC_TTR_URL = "https://online.austrac.gov.au/ao-trn/automatedFileUpload"


MONOOVA_API_ENDPOINT = os.environ.get('MONOOVA_API_ENDPOINT')