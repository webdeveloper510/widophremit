from django.contrib import admin
from django.urls import path,include
from payment_app import views
from payment_app.views import *
from django.conf import settings

#create router object

urlpatterns = [
    ################ Recipient Views ################
    path('create-recipient-validation/', Create_recipient_validation_View.as_view()),
    path('recipient-create/', Recipient_create_View.as_view()),  
    path('recipient-list/', Recipient_list_View.as_view()),
    path('recipient-update/<int:pk>', Recipient_update_View.as_view()),
    path('account-number-validation/', Recipient_account_number_validation.as_view()),  

    ################ Zai PayId Per User Views ################  
    path('zai-payid-register/',  Zai_register_payid_peruser_View.as_view(), name="zai-payid"),
    path('zai-payid/', Zai_payid_per_user_payment_View.as_view(), name="zai-payid"),
    path('zai-payid-details/', Zai_payid_detail_View.as_view(), name="zai-payid-details"),

    ################ Zai PayTo Agreement Views ################  
    path('validate-payid/', Validate_payto_payid_view.as_view(), name="validate-payid"),
    path('zai-create-agreement/', Zai_create_payto_agreement_View.as_view(), name="zai-create-agreement"),
    path('zai-payto/', Zai_payto_agreement_payment_View.as_view(), name="zai-payto"),
    path('zai-agreement-list/', Zai_list_agreement_View.as_view(), name="zai-agreement-list"),
    path('zai-update-agreement/', Zai_update_agreement_View.as_view(), name="zai-update-agreement"),
    path('zai-user-id/', zai_search_email_for_agreement_view.as_view(), name="zai-user-id"),

    ################ Zai Payment Webhooks Views ################  
    path('zai-webhook/', zai_transaction_webhook_View.as_view(), name="zai-webhook"),
    path('zai-agreement-webhook/', zai_agreement_webhook_View.as_view(), name="zai-agreement-webhook"),
    path('zai-payto-payment-webhook/', zai_payto_payment_webhook_View.as_view(), name="zai-payto-payment"),

    ################ Strip Views ################
    #using stripe charge api only for live 
    path('stripe/user-charge/', views.Stripe_one_step_payment_View.as_view(), name="stripe-user-charge"), 
    path('stripe-charge/', views.Stripe_Payment_View.as_view(), name="stripe-charge"), 
    path('new/', Stripe_new_View.as_view(), name="new"),

    ################ Download Payment Receipt Views ################
    path('receipt/<int:pk>', views.Payment_Receipt_View.as_view(), name="receipt"), 
        
    ################ Transaction Views ################  
    path('create-transaction/', Create_Update_Transaction_View.as_view(), name="create-transaction"),
    path('transaction-history/', transaction_history.as_view(), name="transaction-history"),
    path('summary/', transaction_summary.as_view(), name="summary"),
    path('pending-transactions/', Pending_Transactions_View.as_view(), name="pending transaction"),
    path('failed-transactions/', failed_transactions.as_view(), name="completed-transactions"),
    path('previous-transactions/', previous_transactions_View.as_view(), name="zai-payto-payment"),
    path('last-transaction/', last_transaction_view.as_view(), name="last transaction"),
    path('transaction-usage-details/', Transactions_usage_deatils_View.as_view(), name="transaction-usage-details"),

    ################ Referral Views ################  
    path('referrals-list/<str:currency>/', customer_referral_codes_list_view.as_view()),
    path('apply-referral-code/', apply_referral_code_view.as_view()),
    path('referrals/', get_default_referrals_discount_amount.as_view(), name="referrals"),
    path('vouchers/', voucher_view.as_view(), name="vouchers"),

    ################ FN Transaction and Veriff Webhook Views ################  
    path('veriff-webhook/', Veriff_webhook_View.as_view(), name="veriff-webhook"),
    path('fn-webhook-data', FN_webhook_View.as_view(), name="fn-webhook-data"),

    ################ Subscribe newsletter Views ################  
    path('subscribe-newsletter/', Subscribe_newsletter_View.as_view()),

    ################ Card Views ################  
    path('create-card/', stripe_create_card_view.as_view(), name="create-card"),
    path('card-list/', stripe_card_list_view.as_view(), name="card-list"),
    path('card/<int:pk>', stripe_card_update_view.as_view(), name="card-list"),

    ################ Another Views ################  
    path('cloud-currency/login/', views.Cloud_Currency_ViewSet.as_view({'post':'login'})),   
    path('test/', views.test_View.as_view()),   

] 


