from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(currencycloud)
admin.site.register(digital_id)
admin.site.register(fraud_net)
admin.site.register(email_credentials)
admin.site.register(stripecredentials)

@admin.register(Blogs)
class blogs_ModelAdmin(admin.ModelAdmin):
    list_display = ('id','path','image','name','short_description')

