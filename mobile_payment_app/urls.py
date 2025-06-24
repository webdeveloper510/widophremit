from django.contrib import admin
from django.urls import path
from mobile_payment_app import views
from mobile_payment_app.views import *
from django.conf import settings
#create router object

urlpatterns = [
    path('exchange_rate', Exchange_Rate_Converter.as_view(), name='exchange-rate'),
    path('destination_currency', preferred_destination_currency_view.as_view(), name="destination-currency"),
    path('stripe/user_charge', views.Stripe_one_step_payment_View.as_view(), name="stripe-user-charge"), 
    path('payment_confirm_otp', PaymentConfirmOtpView.as_view(), name="payment-confirm-otp"),
    path('receipt/<int:pk>', views.Payment_Receipt_download_View.as_view(), name="receipt"),
    path('recipient_list', Recipient_list_View.as_view(), name="recipient-list"),
    path('recipient_create', Recipient_create_View.as_view(), name="recipient-create"),
    path('recipient_create_v1', Recipient_create_new_View.as_view(), name="recipient-create"),
    path('recipient_update/<int:pk>', Recipient_update_View.as_view(), name="recipient-update"),
    path('recipient_update_v1/<int:pk>', Recipient_update_new_View.as_view(), name="recipient-update"),  
    path('transaction_history', transaction_history.as_view(), name="transaction-history"),
    path('transaction_history_v1', transaction_history_v1.as_view(), name="transaction-history"),
    path('stripe_charge', views.Stripe_Payment_View.as_view(), name="stripe-charge"), 
    path('search', views.SearchViewSet.as_view(),name="search"),
    path('card_token',views.stripe_create_card_view.as_view(), name="card_token"),
    path('stripe/card_token', views.Stripe_old_Payment_ViewSet.as_view({'post':'stripe_card'})),
    path('zai_payid_register',  Zai_register_payid_peruser_View.as_view(), name="zai_payid"),
    path('zai_payid', Zai_payid_per_user_payment_View.as_view(), name="zai_payid"),
    path('zai_create_agreement', Zai_create_payto_agreement_View.as_view(), name="zai_create_agreement"),
    path('zai_payto', Zai_payto_agreement_payment_View.as_view(), name="zai-payto"),
    path('zai_agreement_list', Zai_list_agreement_View.as_view(), name="zai_agreement_list"),
    path('zai_agreement_update', Zai_update_agreement_View.as_view(), name="zai_agreement_list"),
    path('veriff', views.Veriff_view.as_view()),
    path('veriff_verify', VeriffStatus_View.as_view()),
    path('veriff_status_check', veriff_session_decision_View.as_view(), name="veriff"),
    path('transaction_summary', transaction_summary.as_view(), name="summary"),
    # path('verify_check', views.Exchange_check_view.as_view(), name="verify_check"),
    path('summary_v1', transaction_summary_v1.as_view(), name="summary"),
    
    path('create_transaction_mobile_dump', Create_Update_Transaction_Mobile_View.as_view(), name="create-transaction-dump"),
    path('create_transaction', Create_Update_Transaction_View.as_view(), name="create-transaction"),
    path('pending_transactions', Pending_Transactions_View.as_view(), name="pending transaction"),
    path('notification_list', notification_list.as_view()),
    path('vouchers', voucher_view.as_view(), name="vouchers"),

    path('apply_referral_code', apply_referral_code_view.as_view()),
    path('referrals', get_default_referrals_discount_amount.as_view(), name="referrals"),
    path('referrals_list/<str:currency>', customer_referral_codes_list_view.as_view()),

    path('transaction_usage_details', Transactions_usage_deatils_View.as_view(), name="transaction-usage-details"),

]