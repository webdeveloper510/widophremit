from django.urls import path
from mophy import mophy_views
from users import users_views
app_name='mophy'

urlpatterns = [
    ################ Users  ############
    path('users/',users_views.users, name="users"),
    path('new-customers/',users_views.new_customers,name="new-customers"),
    path('delete-user/<str:id>/',users_views.delete_user,name="delete-user"),
    path('enable-user/<str:id>/', users_views.enable_user, name="enable-user"),
    path('user-details/<str:id>/',users_views.user_details,name="user-details"),
    path('add-user/',users_views.add_user,name="add-user"),
    path('update-tier/',users_views.update_tier,name="update-tier"),
    path('update-documents-status/',users_views.update_documents_status,name="update-documents-status"),

    path('create-customer/',users_views.create_customer, name="create-customer"), #pending

    ############ admin users ###########
    path('admin-users/',users_views.admin_users,name="admin-users"),
    path('add-admin-user/',users_views.add_admin_user,name="add-admin-user"),
    path('edit-admin-user/<int:id>/',users_views.edit_admin_user,name="edit-admin-user"),
    path('delete-admin-user/<int:id>/',users_views.delete_admin_user,name="delete-admin-user"),
    path('enable-admin-user/<str:id>/', users_views.enable_admin_user, name="enable-admin-user"),


  ############ Blogs ###########
    path('blogs-list/',users_views.blogs_list, name="blogs-list"),
    path('add-blog/',users_views.create_blog, name="add-blog"),
    path('blog-detail/<int:id>/',users_views.blog_detail, name="blog-detail"),
    path('delete-blog/<int:id>/',users_views.delete_blog, name="delete-blog"),






path('pending-transactions/',users_views.pending_payment_transactions_view, name="pending-transactions"),
path('incomplete-transactions/',users_views.incomplete_transactions, name="incomplete-transactions"),
path('pending-review-processing-transactions/',users_views.pending_review_processing_transactions, name="pending-review-processing-transactions"),
path('approved-transactions/',users_views.approved_transactions, name="approved-transactions"),
path('cancelled-transactions/',users_views.cancelled_transactions, name="cancelled-transactions"),
path('queue-transactions/',users_views.queued_transactions, name="queue-transactions"),
path('transactions/',users_views.transactions,name="transactions"),
path('transaction-activity/',users_views.transaction_activity_report,name="transaction_activity_report"),
path('transaction-monitoring/',users_views.transaction_monitoring, name="transaction-monitoring"),
path('delete-transaction/<str:id>/',users_views.delete_transaction,name="delete-transaction"),
path('transactions-details/<int:id>/',users_views.transactions_details,name="transactions-details"),

path('forex-details/',users_views.forex_details,name="forex-details"),# forex api
path('delete-forex/<int:id>/',users_views.delete_forex,name="delete-forex"),# forex api
path('add-forex/',users_views.add_forex,name="add-forex"),# forex api
path('edit-forex/',users_views.edit_forex,name="edit-forex"),# forex api
path('corridors/',users_views.corridors_details,name="corridors"),
path('edit-user/<str:id>/',users_views.edit_user,name="edit-user"),

path('currency-cloud/',users_views.currency_cloud, name="currency-cloud"),
path('stripe/',users_views.stripe_page, name="stripe"),
path('receipt/<int:id>/',users_views.receipt,name="receipt"),
path('my-wallets/',users_views.my_wallets, name="my-wallets"),
path('zai-transfer/<str:id>/',users_views.zai_transfer, name="zai-transfer"),

path('veriff/',users_views.veriff, name="veriff"),
path('update-veriff-status/',users_views.update_veriff_status, name="update-veriff-status"),

################ Zai #######################################
path('zai/',users_views.zai_home_page, name="zai"),
path('get-zai-wallet/',users_views.zai_wallet_of_user, name="get-zai-wallet"),
path('withdraw-funds/',users_views.withdraw_funds_from_zai, name="withdraw-funds"),


path('add-recipient/<int:id>/',users_views.add_recipient,name="add-recipient"),
path('delete-recipient/<int:id>/',users_views.delete_recipient,name="delete-recipient"),
path('user-transfer/',users_views.zai_user_transfer,name="user-transfer"),
path('get-balance/',users_views.get_zai_balance,name="get-balance"),

path('login/',users_views.login_user,name="login"),
path('logout/',users_views.logout_user,name="logout"),
path('change-password/',users_views.change_password,name="change-password"),
path('send_otp',users_views.send_otp,name="send_otp"),
path('send-reset-password-otp',users_views.send_reset_password_otp,name="send-reset-password-otp"),
# path('forgot-password',users_views.forgot_password,name="forgot-password"),

path('',mophy_views.index,name="index"),
path('index/',mophy_views.index,name="index"),

path('loyality-program/',users_views.loyality_program, name="loyality-program"),
path('delete-loyality-program/<int:id>/',users_views.delete_loyality_program, name="delete-loyality-program"),

path('add-loyality-program/',users_views.add_loyality_program, name="add-loyality-program"),
path('edit-loyality-program/<int:id>',users_views.edit_loyality_program, name="edit-loyality-program"),
path('get_referral_amount/',users_views.get_referral_amount, name="get_referral_amount"),
path('customer-referrals/',users_views.customer_referrals, name="customer-referrals"),
path('referral-detail/<int:id>/',users_views.referral_detail, name="referral-detail"),
path('delete-referral/<int:id>/',users_views.delete_referral, name="delete-referral"),
path('edit-referral/<int:id>/',users_views.edit_referral, name="edit-referral"),

path('ui-alert/',mophy_views.ui_alert,name="ui-alert"),
path('ui-button/',mophy_views.ui_button,name="ui-button"),
path('ui-modal/',mophy_views.ui_modal,name="ui-modal"),
path('ui-button-group/',mophy_views.ui_button_group,name="ui-button-group"),
path('ui-dropdown/',mophy_views.ui_dropdown,name="ui-dropdown"),
path('ui-popover/',mophy_views.ui_popover,name="ui-popover"),
path('ui-pagination/',mophy_views.ui_pagination,name="ui-pagination"),
path('ui-grid/',mophy_views.ui_grid,name="ui-grid"),

path('uc-select2/',mophy_views.uc_select2,name="uc-select2"),
path('uc-sweetalert/',mophy_views.uc_sweetalert,name="uc-sweetalert"),
path('uc-toastr/',mophy_views.uc_toastr,name="uc-toastr"),

path('form-pickers/',mophy_views.form_pickers,name="form-pickers"),

path('page-error-400/',mophy_views.page_error_400,name="page-error-400"),
path('page-error-403/',mophy_views.page_error_403,name="page-error-403"),
path('page-error-404/',mophy_views.page_error_404,name="page-error-404"),
path('page-error-500/',mophy_views.page_error_500,name="page-error-500"),
path('page-error-503/',mophy_views.page_error_503,name="page-error-503"),

path('add-permissions/<int:id>/',users_views.assign_permissions_to_user,name="add-permissions"),

#admin users
path('groups/',users_views.groups_list,name="groups"),
path('group-edit/<int:id>/',users_views.group_edit,name="group-edit"),
path('group-delete/<int:id>/',users_views.group_delete,name="group-delete"),
path('group-add/',users_views.group_add,name="group-add"),
path('add-admin-roles/',users_views.add_admin_roles,name="add-admin-roles"),
path('permissions/',users_views.permissions, name="permissions"),
path('roles/',users_views.roles_list, name="roles"),
path('role-delete/<int:id>/',users_views.role_delete,name="role-delete"),

path('edit-role/<int:id>/',users_views.edit_role, name="edit-role"),
path('search-zai-user/',users_views.search_zai_user, name="search-zai-user"),



path('download-csv/', users_views.download_csv, name="download-csv"),
# path('download-transactions-csv/', users_views.download_transactions_csv, name="download-transactions-csv"),
path('get-csv-values/', users_views.get_csv_values, name="get-csv-values"),
path('set-value/', users_views.set_value, name="set-value"),
path('zai-page/', users_views.new_zai_page, name="zai-page"),
path('wallet-balance/', users_views.ZaiWalletBalance, name="wallet-balance"),
path('search-ra-wallet/', users_views.search_ra_wallet, name="search-ra-wallet"),
path('search-user-wallet/', users_views.search_user_wallet, name="search-user-wallet"),
path('withdraw-zai-funds/', users_views.Withdraw_Funds, name="withdraw-zai-funds"),
path('transfer-funds',users_views.transfer_funds, name="transfer-funds"),

path('payout-list',users_views.payout_accounts_list, name="payout-list"),
path('add-payout-account',users_views.add_payout_account, name="add-payout-account"),
path('link-bank-account',users_views.link_bank_account, name="link-bank-account"),
path('confirm-details',users_views.confirm_details, name="confirm-details"),
path('payout-transactions/<str:id>',users_views.payout_transactions, name="payout-transactions"),
path('ra-payout',users_views.zai_ra_payout, name="ra-payout"),
path('get-payout-balance',users_views.get_payout_wallet_balance, name="get-payout-balance"),
path('edit-payout-account/<str:id>',users_views.edit_payout_account, name="edit-payout-account"),
path('austrac',users_views.austrac, name="austrac"),


]
