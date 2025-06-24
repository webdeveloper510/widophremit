from django.urls import path
from auth_app.views import *
from auth_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    ######################## Registration Process Views ######################
    path('register-check/', RegistrationCheck.as_view(),name='register-check'),
    path('register-verify/', RegistrationVerify.as_view(),name='register-verify'),
    path('send-signup-emails/', SendRegistrationEmails.as_view(), name="send-signup-emails"),
    path('resend-register-otp/', ResendSignupOtp.as_view(),name='resend-register-otp'),

    ########################## Activate email Views ##########################   
    path('activate-email/',  EmailActivation.as_view(), name='activate-email'),

    ########################## Login Process Views ###########################
    path('login/',Login.as_view(),name='login'),
    path('verify-email/', Verify_OTP.as_view(), name='verify-email'),

    ################### Send/Resend Otp on all places Views ##################
    path('resend-otp/', Resend_OTP.as_view(), name='resend-otp'),

    ############################## Profile Views #############################
    path('user-profile/', Profile.as_view(),name='userprofile'),
    path('update-profile/', UpdateProfile.as_view(), name='auth_update_profile'),
    path('delete-user/<int:pk>', DeleteUser.as_view(), name="delete-user"),
    path('user-exist/', Is_User_Exists.as_view(), name="user-exist"),

    ############################ Password Views #############################
    path('change-password/', ChangePassword.as_view(),name='changepassword'),
    path('send-password-reset-email/', SendResetPasswordEmail.as_view(), name='send-reset-password-email'),
    path('reset-password/',  ResetPassword.as_view(), name='reset-password'),

    ########################### Invite User Views ##########################
    path('invite-email/', SendInviteEmail.as_view(), name="invite-email"),
    path('referral-link/', ReferralLink.as_view(), name='referral-link'),

    ################## FX / Exchange Rate Converter Views ##################
    path('exchange-rate/', ExchangeRateConverter.as_view(), name='exchange-rate'),

    ################ Preferred Currency Pair of User Views #################
    path('destination-currency/', Preferred_Destination_Currency.as_view(), name="destination-currency"),

    ################### KYC /Digital Verification Views ####################
    path('digital-verification/', DigitalId.as_view(), name='digital-verification'),
    path('is-digitalid-verified/', IsDigitalIdVerified.as_view(), name='is-digitalid-verified'),

    ########################## KYC / Veriff Views ##########################
    path('veriff/', VeriffSessionDecision.as_view(), name="veriff"),
       
    ########################### Decode Data Views ##########################
    path('decode/', Decode.as_view(), name="decode"),

    ########################### Contact Us ##########################
    path('contact-us/', ContactUsView.as_view(), name="contact-us"),

    ########################### Update Tier ##########################
    path('update-tier/', Update_tier_request_view.as_view(), name="update-tier"),

]

######## Media and Static URL ##########
if settings.DEBUG == True or settings.DEBUG == False:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

