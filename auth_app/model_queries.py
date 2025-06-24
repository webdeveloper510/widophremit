from rest_framework_simplejwt.tokens import RefreshToken
import random
from django.conf import settings
from auth_app.models import *
from django.db.models import F, ExpressionWrapper, fields, Value, CharField, Avg
from django.db.models.functions import Concat


""" CREATE OBJECT IN MODEL """
def create_model_obj(model, data):
    return model.objects.create(**data)

""" UPDATE OBJECT IN MODEL """ 
def update_model_obj(model, filter_key, data):
    return model.objects.filter(**filter_key).update(**data)

""" GET OBJECT FROM MODEL """ 
def filter_model_objs(model, filter_key, data=None):
    if data is not None:
        values = model.objects.filter(**filter_key).values(*data)
    else:
        values = model.objects.filter(**filter_key)
    return values

def get_all_filter_values(model, filter_key):
    values = model.objects.filter(**filter_key).values()
    return values

def get_all_model_obj(model, data=None):
    if data == None:
        return model.objects.all()
    values = model.objects.all().values(*data)
    return values

def get_all_annotate_model_obj(model, annotate, data):
    values = model.objects.all().annotate(**annotate).values(*data)
    return values

def filter_annotate_model_obj(model, filter_key, annotate, data):
    values = model.objects.filter(**filter_key).annotate(**annotate).values(*data)
    return values

""" TO CHECK IS OBJECT EXISTS IN MODEL OR NOT """ 
def is_obj_exists(model, filter_key):
    return model.objects.filter(**filter_key).exists()

