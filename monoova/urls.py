from django.contrib import admin
from django.urls import path
from monoova.views import *
from django.conf import settings


urlpatterns = [
    path('direct-credit/', DirectCreditView.as_view(), name='direct_credit'),
    path('direct-debit/', DirectDebitView.as_view(), name='direct_debit'),
]