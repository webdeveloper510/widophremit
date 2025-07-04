from django import forms
from users.models import User
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordResetForm
from payment_app.models import *
from payment_app.serializers import *
from service_providers.models import *
from Widoph_Remit.package import *

import phonenumbers as pn 
from phonenumbers import geocoder 
  
class stripeform(forms.ModelForm):
    publish_key = forms.CharField(required=False)
    secret_key = forms.CharField(required=False)
    url = forms.URLField(required=False)
    MODE = (
        ('sandbox', 'sandbox'),
        ('live', 'live'),
    )
    STATUS = (
        ('enabled', 'enabled'),
        ('disabled', 'disabled'),
    )
    mode = forms.ChoiceField(choices=MODE, required=False)
    status = forms.ChoiceField(choices=STATUS, required=False)

    class Meta:
        model = stripecredentials
        fields = ('publish_key',
                  'secret_key',
                  'url',
                  'mode',
                  'status',
        )

    def save(self):
        obj = super().save()
        cleaned_data = super().clean()
        publish_key = cleaned_data.get('publish_key')
        secret_key = cleaned_data.get('secret_key')
        url = cleaned_data.get('url')
        mode = cleaned_data.get('mode')
        status = cleaned_data.get('status')
        dict = {'obj':obj, 'publish_key':publish_key, 'secret_key':secret_key, 'url':url, 'mode':mode, 'status':status}
        return dict

class currencycloudform(forms.ModelForm):
    login_id = forms.CharField(required=False)
    api_key = forms.CharField(required=False)
    url = forms.URLField(required=False)
    MODE = (
        ('sandbox', 'sandbox'),
        ('Live', 'live'),
    )
    STATUS = (
        ('enabled', 'enabled'),
        ('disabled', 'disabled'),
    )
    mode = forms.ChoiceField(choices=MODE, required=False)
    status = forms.ChoiceField(choices=STATUS, required=False)

    class Meta:
        model = currencycloud
        fields = ('login_id',
                  'api_key',
                  'url',
                  'mode',
                  'status'
                )
      
    def save(self):
        # Save the provided password in hashed format
        obj = super().save()
        cleaned_data = super().clean()
        login_id = cleaned_data.get('login_id')
        api_key = cleaned_data.get('api_key')
        url = cleaned_data.get('url')
        mode = cleaned_data.get('mode')
        status = cleaned_data.get('status')
        dict = {'obj':obj, 'login_id':login_id, 'api_key':api_key, 'url':url, 'mode':mode, 'status':status}
        return dict


class transaction_activity_form(forms.ModelForm):
    send_currency = forms.CharField(required=False)
    recieve_currency = forms.CharField(required=False)

    class Meta:
        model = Transaction_details
        fields = ('send_currency',
                  'recieve_currency',
                )


#Add User Form
GENDER_CHOICES = (
    ('','Choose gender'),
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Others', 'Others'),
    )

LOCATION_CHOICES = [('', 'Choose Location')] + [(key, key) for key in settings.USER_COUNTRIES]

class NewUserForm(forms.ModelForm):
    First_name = forms.CharField(required=True)
    Middle_name = forms.CharField()
    Last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    mobile = forms.CharField(required=True)
    Date_of_birth = forms.CharField(required=True)
    # Gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    location = forms.ChoiceField(choices=LOCATION_CHOICES, required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',
                  'First_name',
                  'Middle_name',
                  'Last_name',
                #   'Gender',
                  'Date_of_birth',
                  'mobile',
                  'email',
                  'location',
                  'password'
                )
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile') 
        if User.objects.filter(mobile__icontains=mobile, is_superuser=False).exists():
            raise forms.ValidationError('This mobile number is already registered.')
        return mobile
    
    def clean_password2(self):
        # Check that the two password entries match
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

    # def save(self):
    #     # Save the provided password in hashed format
    #     user = super().save()
    #     user.save()
    #     return user

RECIPIENT_COUNTRIES = [('', 'Choose Location')] + [(key, key) for key in settings.RECIPIENT_COUNTRIES]

class NewRecipientBankForm(forms.ModelForm):
    recipient_id = forms.IntegerField(required=True)
    bank_name = forms.CharField(required=True)
    account_name = forms.CharField(required=True)
    account_number = forms.CharField(required=True)
    swift_code = forms.EmailField(required=True)
    bank_address = forms.CharField(required=True)
  
    class Meta:
        model = Recipient
        fields = ('recipient_id',
                  'bank_name',
                  'account_name',
                  'account_number',
                  'swift_code',
                  'bank_address'
                )
        
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

class NewRecipientForm(forms.ModelForm):
    user_id = forms.IntegerField(required=False)
    first_name = forms.CharField(required=True)
    middle_name = forms.CharField(required=False)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    mobile = forms.CharField(required=True)
    flat = forms.CharField(required=False)
    building = forms.CharField(required=False)
    street = forms.CharField(required=True)
    postcode = forms.CharField(required=True)
    city = forms.CharField(required=True)
    state = forms.CharField(required=True)
    country = forms.ChoiceField(choices=RECIPIENT_COUNTRIES, required=True)

    class Meta:
        model = Recipient
        fields = ('email',
                  'first_name',
                  'middle_name',
                  'last_name',
                  'mobile',
                  'flat',
                  'building',
                  'street',
                  'postcode',
                  'city',
                  'state',
                  'country'
                )
        
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile') 
        if Recipient.objects.filter(mobile__icontains=mobile).exists():
            raise forms.ValidationError('This mobile number is already registered.')
        return mobile
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class EdittransactionForm(forms.ModelForm):
    CHOICES = (
        ('pending', 'pending'),
        ('completed', 'completed'),
        ('failed', 'failed'),
    )
    customer_id = forms.CharField(required=False)
    send_currency = forms.CharField(required=False)
    recieve_currency = forms.CharField(required=False)
    amount = forms.CharField(required=False)
    send_method = forms.CharField(required=False)
    recieve_method = forms.CharField(required=False)
    status = forms.ChoiceField(choices=CHOICES, required=False)
    reason = forms.CharField(required=False)
    day = forms.CharField(required=False)
    recipient_name = forms.CharField(required=False)

    class Meta:
        model = Transaction_details
        fields = ('customer_id',
                  'send_currency',
                  'recieve_currency',
                  'amount',
                  'send_method',
                  'recieve_method',
                  'status',
                  'reason',
                  'day',
                  'recipient_name'
                )
      
    # def save(self):
    #     cleaned_data = super().clean()
    #     status = cleaned_data.get('status')
    #     return status

class EditUserForm(forms.ModelForm):
    First_name = forms.CharField()
    Middle_name = forms.CharField()
    Last_name = forms.CharField()
    Date_of_birth = forms.CharField()
    mobile = forms.CharField()
    customer_id = forms.CharField(required=False, disabled=True)
    email = forms.EmailField(required=False)
    mobile = forms.CharField(required=False)
    Date_of_birth = forms.CharField(required=False)
    location = forms.ChoiceField(choices=LOCATION_CHOICES, required=False)

    class Meta:
        model = User
        fields = ('email',
                  'First_name',
                  'Middle_name',
                  'Last_name',
                  'customer_id',
                  'Date_of_birth',
                  'mobile',
                  'location'
                )
    
    # def clean_mobile(self):
    #     mobile = self.cleaned_data.get('mobile') 
    #     print(mobile, "mobile = = = =")
    #     if User.objects.filter(mobile__icontains=mobile, is_superuser=False).exists():
    #         print("yessssssssssssssss===========")
    #     #     raise forms.ValidationError('This mobile number is already registered.')
    #     return mobile
      
    def save(self):
        # Save the provided password in hashed format
        user = super().save()
        return user




class LoginForm(forms.Form):
    email =  forms.EmailField()
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        User.objects.filter(email=email).update(updated_at=timezone.now())
        if not user or not user.is_active:
            raise forms.ValidationError("Sorry, that login was invalid. Please try again.")
        return self.cleaned_data
        
    def login(self, request):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        return user
        

class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("There is no user registered with the specified email address!")
        return email


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name','permissions')

class PermissionsForm(forms.ModelForm):
    name = forms.CharField(label='Name', help_text="Example: Can action modelname")
    codename = forms.CharField(label='Code Name', help_text="Example: action_modelname")

    class Meta:
        model = Permission
        fields = ('name','codename','content_type')


class UserPermissionsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('user_permissions',)

ROLES = (
    ('','Choose Role'),
    ('staff'  , 'Staff'),
    ('admin', 'Admin'),
    )

class AddAdminUserForm(forms.ModelForm):
    First_name = forms.CharField(required=True)
    Middle_name = forms.CharField(required=False)
    Last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    mobile = forms.CharField(required=True)
    location = forms.ChoiceField(choices=LOCATION_CHOICES, required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',
                  'First_name',
                  'Middle_name',
                  'Last_name',
                  'mobile',
                  'email',
                  'location',
                  'password'
                )
        
    def clean_email(self):
        email = self.cleaned_data.get('email') 
        if User.objects.filter(email__icontains=email, is_superuser=True).exists():
            raise forms.ValidationError('Email already registered.')
        return email
    
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile') 
        print(mobile, "mobile===")
        if User.objects.filter(mobile__icontains=mobile, is_superuser=True).exists():
            print("mobile exists")
            raise forms.ValidationError('This mobile number is already registered.')
        return mobile
    
    def clean_password2(self):
        # Check that the two password entries match
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name','permissions')