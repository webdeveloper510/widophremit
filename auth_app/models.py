from django.db import models
import secrets
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager 
from django.core.validators import RegexValidator
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

#  Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, location, mobile, password=None ):
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(
            email = self.normalize_email(email),
            location = location,
            mobile = mobile,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        random_code = secrets.token_hex(4)
        user = self.create_user(
            email,
            location="None",
            mobile="0000000000",
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user
 
#  Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    customer_id = models.CharField(max_length=20, null=True, unique=True)
    email = models.EmailField(verbose_name='Email', max_length=200, unique=True)
    First_name = models.CharField(max_length=250)
    Middle_name = models.CharField(max_length=250)
    Last_name = models.CharField(max_length=250)
    Date_of_birth = models.CharField(max_length=250)
    Identity_type = models.CharField(max_length=250)
    Gender = models.CharField(max_length=250)
    Country_of_birth = models.CharField(max_length=250)
    mobile = models.CharField(max_length=30)
    location = models.CharField(max_length=250)
    referred_by = models.CharField(max_length=250, blank=True, null=True)
    referral_code = models.CharField(max_length=250, blank=True, null=True, unique=True)
    promo_marketing = models.BooleanField(default=False)
    email_otp = models.CharField(max_length=250, null=True, unique=True)
    otp = models.CharField(max_length=20, null=True)
    country_code = models.CharField(max_length=30)
    is_verified = models.BooleanField(default=False)
    is_digital_Id_verified = models.CharField(max_length=250, default="pending")
    aml_pep_status = models.BooleanField(null=True, blank=True)
    mobile_verified = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    stripe_customer_id = models.CharField(max_length=250)
    transactions = models.IntegerField(null=True, blank=True, default=0)
    occupation = models.CharField(max_length=250, null=True, blank=True)
    payment_per_annum = models.CharField(max_length=250, null=True, blank=True)
    value_per_annum = models.CharField(max_length=250, null=True, blank=True)
    source_currency = models.CharField(max_length=250, null=True, blank=True)
    destination_currency = models.CharField(max_length=250, null=True, blank=True)
    fcm_token = models.CharField(max_length=300, null=True, blank=True)
    user_type = models.CharField(max_length=250, null=True, blank=True)
    apps_version = models.CharField(max_length=250, null=True, blank=True)
    app_update = models.BooleanField(default=False, null=True, blank=True)
    platform = models.CharField(max_length=250, null=True, blank=True)
    user_check = models.CharField(max_length=250, null=True, blank=True)
    documents = models.CharField(max_length=250, null=True, blank=True, default='not_required')
    objects = UserManager()

    USERNAME_FIELD = 'email'
  
    def __str__(self):
        return self.email

   
IMAGE_TITLE = [
    ("Logo", "Logo"),
    ("Footer", "Footer"),
    ("Welcome", "Welcome"),
    ("Img01", "Img01"),
    ("OTP", "OTP"),
    ("Refer_signup", "Refer_signup"),
    ("Earn_voucher", "Earn_voucher"),
    ("Verify_Email_Logo", "Verify_Email_Logo"),
    ("Facebook", "Facebook"),
    ("Twitter", "Twitter"),
    ("Instagram", "Instagram"),
    ("Linkedin", "Linkedin"),
    ("Notification_Logo", "Notification_Logo"),
    ("New_Customer", "New_Customer"),
    ("Transaction_Notification", "Transaction_Notification"),
    ("Sender_Transaction_Notification", "Sender_Transaction_Notification")

]

class Email_template_images(models.Model):
    title = models.CharField(choices = IMAGE_TITLE, max_length=150, default="Logo")
    image = models.ImageField(upload_to ='email_template')
    def __str__(self):
        return "{} -{}-".format(self.image, self.title)
    class Meta:
           verbose_name_plural = "Email Template Images"

class User_address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flat = models.CharField(max_length=250, null=True, blank=True)
    building = models.CharField(max_length=250, null=True, blank=True)
    street = models.TextField(max_length=5000, null=True, blank=True)
    postcode = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=250, null=True, blank=True)
    state = models.CharField(max_length=250, null=True, blank=True)
    country_code = models.CharField(max_length=250, null=True, blank=True)
    country = models.CharField(max_length=250, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "User address"

    def __str__(self):
        return "{}".format(self.id)


class Application_AI(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    risk_group = models.CharField(max_length=250, null=True, blank=True)
    risk_score = models.CharField(max_length=250, null=True, blank=True)
    rule_name = models.CharField(max_length=1000, null=True, blank=True)
    comply_adv = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "User address"

    def __str__(self):
        return "{}".format(self.id)
    
class Digital_id_details(models.Model):
    customer_id = models.CharField(max_length=90)
    customer_name = models.CharField(max_length=90)
    transaction_id = models.CharField(max_length=90)
    sub = models.CharField(max_length=90)
    iss = models.CharField(max_length=90)
    aud = models.CharField(max_length=90)   
    dob = models.CharField(max_length=90)
    street = models.CharField(max_length=90)
    locality = models.CharField(max_length=90)
    region = models.CharField(max_length=90)
    postal_code = models.CharField(max_length=90, null=True, blank=True)
    country = models.CharField(max_length=90)
    address_verified = models.BooleanField(default=False)
    name = models.CharField(max_length=200, null=True, blank=True)
    updated_at = models.CharField(max_length=90)
    exp = models.CharField(max_length=90)
    iat = models.CharField(max_length=90)

    class Meta:
           verbose_name_plural = "Digital id details"


class Registration_otp(models.Model):
    mobile = models.CharField(max_length=90)
    otp = models.CharField(max_length=90)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}".format(self.mobile)
    
    class Meta:
           verbose_name_plural = "Temporary Registration OTP"

class notification(models.Model):
    source_id = models.CharField(max_length=90)
    source_type = models.CharField(max_length=90)
    source_detail = models.CharField(max_length=90)
    message = models.TextField(max_length=500)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.id)
    
    class Meta:
           verbose_name_plural = "Notifications"

class Veriff(models.Model):
    customer_id = models.CharField(max_length=90)
    first_name = models.CharField(max_length=90, null=True, blank=True)
    last_name = models.CharField(max_length=90, null=True, blank=True)
    id_type = models.CharField(max_length=90, null=True, blank=True)   
    id_number = models.CharField(max_length=90, null=True, blank=True)
    id_country = models.CharField(max_length=90, null=True, blank=True)
    ip = models.CharField(max_length=90, null=True, blank=True)
    status = models.CharField(max_length=90, null=True, blank=True)
    session_id = models.CharField(max_length=350, null=True, blank=True)
    reason = models.CharField(max_length=350, null=True, blank=True)
    doc_valid_from = models.CharField(max_length=90, null=True, blank=True)
    doc_valid_until = models.CharField(max_length=90, null=True, blank=True)
    state = models.CharField(max_length=90, null=True, blank=True)
    dob = models.CharField(max_length=90, null=True, blank=True)
    gender = models.CharField(max_length=90, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Veriff "


class Veriff_media(models.Model):
    customer_id = models.CharField(max_length=90)
    session_id = models.CharField(max_length=350, null=True, blank=True)
    media_id = models.CharField(max_length=350, null=True, blank=True)
    path = models.CharField(max_length=350, null=True, blank=True)
    name = models.CharField(max_length=350, null=True, blank=True)
    type = models.CharField(max_length=350, null=True, blank=True)
    image = models.ImageField(upload_to='veriff_media/', blank=True, null=True)
    video = models.FileField(upload_to='veriff_media/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
           verbose_name_plural = "Veriff Media"

    def save(self, *args, **kwargs):
        if self.image and not self.path:
            self.path = settings.BASE_URL+self.image.url
        elif self.video and not self.path:
            self.path = settings.BASE_URL+self.video.url
        super(Veriff_media, self).save(*args, **kwargs)

class Invites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(verbose_name='Email', max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
       
    class Meta:
           verbose_name_plural = "Invites By User "



class roles(models.Model):
    name = models.CharField(max_length=90, null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "{}".format(self.name)
    
    class Meta:
           verbose_name_plural = "Roles"

class permission(models.Model):
    name = models.CharField(max_length=300)
    codename = models.CharField(max_length=300)

    def __str__(self):
        return "{}".format(self.id)
    
    class Meta:
           verbose_name_plural = "Permissions"

class role_permissions(models.Model):
    role = models.ForeignKey(roles, on_delete=models.CASCADE)
    permission = models.ForeignKey(permission, on_delete=models.CASCADE)
    delete = models.BooleanField(null=True, blank=True, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.role)
    
    class Meta:
           verbose_name_plural = "Role Permissions"

class admin_roles(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(roles, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.id)
    
    class Meta:
           verbose_name_plural = "Admins with Roles"


class Contact_us(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    email = models.EmailField(verbose_name='Email', max_length=200)   
    mobile = models.CharField(max_length=250, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.id)
class Tiers(models.Model):
    customer_id = models.CharField(max_length=250, null=True, blank=True)
    old_tier = models.CharField(max_length=250, null=True, blank=True) 
    new_tier = models.CharField(max_length=250, null=True, blank=True)   
    type = models.CharField(max_length=250, null=True, blank=True)   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}".format(self.customer_id)
