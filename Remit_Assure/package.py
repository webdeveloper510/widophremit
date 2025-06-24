from django.shortcuts import render
from rest_framework import viewsets
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
import requests
from django.http import JsonResponse
from rest_framework.response import Response
from auth_app.serializers import *
import stripe
from django.conf import settings
from Remit_Assure.settings import *
from rest_framework import status
from requests_toolbelt import MultipartEncoder
from auth_app.models import *
from auth_app.serializers import *
from payment_app.models import *
from payment_app.serializers import *
from auth_app.renderer import UserRenderer
from auth_app.serializers import UserProfileSerializer
from rest_framework.views import APIView
import json
from datetime import date
from itertools import chain
from Remit_Assure.response import *
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal
import urllib.parse
import secrets
import string
import pytz
import sys, os
import json
from payment_app.models import *
from django.db.models import Count
import hashlib
import hmac
import base64


#auth_app
from django.db.models import Q
from django.http import HttpResponse
from distutils import errors
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from auth_app.renderer import UserRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from django.core.mail import send_mail
from auth_app.models import *
from auth_app.serializers import *
from tokenize import TokenError
from django.utils.encoding import smart_str,force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from auth_app.utils import Util
from django.core.mail import EmailMultiAlternatives, message
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect
# from django.utils import six
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from datetime import timedelta
import datetime
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import update_last_login
import requests
import json
from django.http import JsonResponse
import pdb
import imaplib
from email.message import Message
from time import time
import smtplib
from email.message import EmailMessage
import random
import jwt
import sys
from django.views.decorators.csrf import csrf_exempt
from requests_toolbelt import MultipartEncoder
import os
from email.mime.image import MIMEImage
from django.template.loader import render_to_string
import stripe
import ssl
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from django.template.loader import get_template
from django.template.loader import render_to_string
from payment_app.models import *
from payment_app.serializers import *
import stripe
import ssl
import datetime
from Remit_Assure.response import *
from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML, CSS
from auth_app.sendsms import *
import json
import socket
import json
#mophy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from users.models import User
from users.forms import *
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, permission_required 
from django.contrib.auth.models import Group, Permission
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from users.tokens import account_activation_token
from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import smart_str,force_bytes, DjangoUnicodeDecodeError
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponseRedirect
from payment_app.models import *
from payment_app.serializers import *
from service_providers.models import *
from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML, CSS
from django.db.models import Sum
from django.core import serializers
import json
import datetime
from auth_app.serializers import *
from collections import OrderedDict
from datetime import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect
from payment_app.models import *
import requests
from datetime import date, timedelta
from payment_app.models import *
from django.shortcuts import render, redirect
from django.http import JsonResponse
from datetime import datetime
from dateutil import parser

referral_dict = settings.REFERRALS