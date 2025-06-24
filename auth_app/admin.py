from django.contrib import admin
from auth_app.models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

admin.site.register(Digital_id_details)

class UserModelAdmin(BaseUserAdmin):
    list_display = ('id','stripe_customer_id','customer_id','email','First_name','Middle_name','Last_name','Date_of_birth','Identity_type','Gender',
                    'Country_of_birth','country_code','mobile','location', 'email_otp', 'otp', 'password','is_digital_Id_verified',
                        'referred_by', 'fcm_token','mobile_verified', 'aml_pep_status','referral_code','promo_marketing','is_admin','delete', 'occupation', 'payment_per_annum', 'value_per_annum','transactions','destination_currency')
    list_filter = ('is_admin',)
    fieldsets = (
        ('UserCredentials', {'fields': ('email', 'password')}),
        ('Permissions',{'fields':('is_staff','is_active','is_superuser','groups','user_permissions')}),
        ('Personal',{'fields':('phone_number','about',)}),   
         )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email','password', 'customer_id','mobile','email_otp','is_digital_Id_verified', 'referred_by' 'referral_code','promo_marketing')
        }),
    )
    search_fields = ('email','first_name','last_name','middle_name')
    ordering = ('email','id')
    filter_horizontal = ()

# Now register the new UserModelAdmin...
admin.site.register(User, UserModelAdmin)

@admin.register(Email_template_images)
class Email_template_imagesModelAdmin(admin.ModelAdmin):
  list_display = ('id','title','image','display')

  def display(self, obj):
     return format_html(f'<img src="/media/{obj.image}" style="height:30px;">')

@admin.register(User_address)
class User_address_ModelAdmin(admin.ModelAdmin):
    list_display = ('id','user','flat','building','street', 'postcode','city','state','country_code','country')

@admin.register(Registration_otp)
class User_address_ModelAdmin(admin.ModelAdmin):
    list_display = ('id','mobile','otp', 'created_at')

@admin.register(notification)
class notification_ModelAdmin(admin.ModelAdmin):
    list_display = ('id','source_id','source_type', 'source_detail','message','read','created_at')

admin.site.register(Veriff)
admin.site.register(Invites)
admin.site.register(permission)

@admin.register(Veriff_media)
class veriff_media_ModelAdmin(admin.ModelAdmin):
    list_display = ('id','customer_id','path','image', 'video','type')

