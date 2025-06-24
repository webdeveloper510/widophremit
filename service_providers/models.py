from django.db import models
from django.conf import settings

MODE = [
    ("sandbox", "sandbox"),
    ("Live", "Live"),
]
class currencycloud(models.Model):
    mode = models.CharField(choices = MODE, max_length=300, default="sandbox")
    login_id = models.CharField(max_length=300)
    api_key = models.CharField(max_length=300)
    url = models.URLField(max_length=300)
    status =models.CharField(max_length=300)
  
    class Meta:
        verbose_name_plural = "Currency Cloud"

    def __str__(self):
        return "{}".format(self.id)

class digital_id(models.Model):
    mode = models.CharField(choices = MODE, max_length=300, default="sandbox")
    type = models.CharField(max_length=300)
    client_id = models.CharField(max_length=300)
    client_secret = models.CharField(max_length=300)
    public_key = models.CharField(max_length=300)
    url = models.URLField(max_length=300)
    status =models.CharField(max_length=300)

    class Meta:
        verbose_name_plural = "Digital Id"

    def __str__(self):
        return "{}".format(self.id)
    
class fraud_net(models.Model):
    mode = models.CharField(choices = MODE, max_length=300, default="sandbox")
    type = models.CharField(max_length=300)
    secret_key = models.CharField(max_length=300)
    access_key = models.CharField(max_length=300)
    url = models.URLField(max_length=300)
    status = models.CharField(max_length=300)

    class Meta:
        verbose_name_plural = "Fraud.net"

    def __str__(self):
        return "{}".format(self.id)

class stripecredentials(models.Model):
    mode = models.CharField(choices = MODE, max_length=300, default="sandbox")
    publish_key = models.CharField(max_length=300)
    secret_key = models.CharField(max_length=300)
    url = models.URLField(max_length=300)
    status = models.CharField(max_length=300)

    class Meta:
        verbose_name_plural = "Stripe Credentials"

    def __str__(self):
        return "{}".format(self.id)
    
class email_credentials(models.Model):
    type = models.CharField(max_length=300)
    server = models.CharField(max_length=300)
    port = models.CharField(max_length=300)
    username = models.CharField(max_length=250)
    password = models.CharField(max_length=250)
  
    class Meta:
        verbose_name_plural = "Email Credentials"

    def __str__(self):
        return "{}".format(self.type)

class zai_credentials(models.Model):
    mode = models.CharField(choices = MODE, max_length=300, default="sandbox")
    client_id = models.CharField(max_length=300)
    client_secret = models.CharField(max_length=300)
    url = models.URLField(max_length=300)
    status = models.CharField(max_length=300)
  
    class Meta:
        verbose_name_plural = "Zai Credentials"

    def __str__(self):
        return "{}".format(self.mode)

class Blogs(models.Model):
    name = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    short_description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='blogs/', blank=True, null=True)
    path = models.CharField(max_length=350, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
           verbose_name_plural = "Blogs"

    def save(self, *args, **kwargs):
        if self.image and not self.path:
            self.path = settings.BASE_URL+self.image.url
            super(Blogs, self).save(*args, **kwargs)

