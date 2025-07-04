from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from users import users_views
from django.contrib.auth import views as auth_views
from users.forms import EmailValidationOnForgotPassword

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('auth_app.urls')),
    path('payment/', include('payment_app.urls')),
    path('adminpanel/',include('mophy.urls', namespace='mophy')),
    path('mobile_app/', include('mobile_app.urls')),
    path('mobile_payment/',include('mobile_payment_app.urls')),
    path('service/',include('service_providers.urls')),
    path('reset_password/',  auth_views.PasswordResetView.as_view(form_class=EmailValidationOnForgotPassword),name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password/', users_views.change_password, name='change_password'),
    path('monoova/',include('monoova.urls')),
]
if settings.DEBUG == True or settings.DEBUG == False:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns.insert(0, path('__debug__/', include(debug_toolbar.urls)))
#     # urlpatterns +=  path('__debug__/', include('debug_toolbar.urls'))

admin.site.site_header  =  "Dashboard"  
admin.site.site_title  =  "Dashboard"
admin.site.index_title  =  "Dashboard"
