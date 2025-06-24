from django.urls import path
from mobile_app.views import *
from mobile_app import views
from django.conf import settings
from django.conf.urls.static import static
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    
    #MobileApi Urls
    path('register', RegisterView.as_view(), name='registeration'),
    path('register_verify_v1', RegistrationVerify.as_view(), name='register-verify-view'),
    path('send_sign_emails', SendRegistrationEmails.as_view(), name="send-signup-emails"),
    path('register_verify', Register_verify_View.as_view(), name='register-verify-view'),
    path('resend_register_otp', Resend_signup_otp_View.as_view(),name='resend-register-otp'),
    path('login_api', LoginView.as_view(), name='loginView'),
    path('verify_login', VerifyMobileView.as_view(), name="verifylogin"),
    path('user_profile', ProfileView.as_view(), name = 'profile'),
    path('update_profile_v1', UpdateProfile.as_view(), name='update-profile'),
    path('update_profile', Update_profile_view.as_view(), name="updateprofile"),
    path('get_reset_otp', GetResetOtpMobileView.as_view(), name='send-reset-password-mobile'),
    path('reset_password_otp_verify', ResetConfirmOtpView.as_view(), name='reset-password'),
    path('update_password', ForgotPassword.as_view(), name='forgot-password'),
    path('change_password', ChangePasswordView.as_view(),name='changepassword'),
    path('resend_otp', Resend_OTP_View.as_view(), name='resend-otp'),
    path('user_exist', Is_User_Exists.as_view(), name="user-exist"),
    path('test_get_otp', TestOtp.as_view(), name="test"),
    path('referral_link', ReferralLink.as_view(), name='referral-link'),
    path('update_tier', Update_tier_request_view.as_view(), name="update-tier"),

    # path("login_notify",views.login_notify),
    # path('test_notify', views.SendNotify.as_view())
]

if settings.DEBUG == True or settings.DEBUG == False:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

