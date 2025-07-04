
from .helpers import *
from auth_app.model_queries import *
from payment_app.views import generate_pdf_receipt
from Widoph_Remit.helpers import error_logs, success_logs, get_current_datetime
from payment_app.helper import create_zai_bank_account, zai_create_user,zai_update_user

transaction =  TRANSACTION
fn_approved = "approved"
fn_queued = "queued"
fn_cancelled = "cancelled"
user_countries = USER_COUNTRIES
recipient_countries =  RECIPIENT_COUNTRIES
referral_dict = REFERRALS

################################################### Permission and Notifications ############################################

""" Permissions of logged in user to show and hide adminpanel modules """
def permissions(request):
	try:
		message = None
		permissions_list = None
		all_perm_count = permission.objects.all().count()
		all_permissions = list(permission.objects.all().values('id','codename','name'))
		filtered_permissions = []
		if is_obj_exists(admin_roles, {'user_id':request.user.id}):
			roles = list(admin_roles.objects.filter(user_id=request.user.id).values('role_id'))
			permissions_list = list(role_permissions.objects.filter(role=roles[0]['role_id'], delete=False).values('permission_id__id','permission_id__codename','permission_id__name'))
			search_values = [item['permission_id__id'] for item in permissions_list]
			filtered_permissions = [perm for perm in all_permissions if perm['id'] not in search_values]
			for x in filtered_permissions:
				x['codename'] = str(x['codename']).replace(x['name']+"_","")
		else:
			filtered_permissions =  list(permission.objects.all().values('id','codename','name'))
			for x in filtered_permissions:
				x['codename'] = str(x['codename']).replace(x['name']+"_","")
		if all_perm_count == len(filtered_permissions):
			message = "You do not have permission to view all resources"
		return JsonResponse({'success':True, 'is_admin':request.user.is_admin, 'message':message, 'permissions_list':filtered_permissions})
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

""" error html page to show if user has no permission """
def page_error_403(request):
    return render(request,'403.html')
    
""" notifications of customer and transactions for all pages """
def notifications(request):
	try:
		notification_data = list(notification.objects.filter(read=False).values().order_by('-created_at'))
		if not notification_data:
			notifications = {"notification_data": "No data found"}
			return notifications
		else:
			for x in notification_data:
				if str(x['source_type']).lower() == "mobile_transaction":
					x['source_type'] = "transaction"
				for key in x:
					x[key] = str(x[key])
			all_count = notification.objects.filter(read=False).count()
			read_notifications = notification.objects.filter(read=True)
			read_notifications.delete()
			notifications = {
				"notification_data": notification_data,
				"all_count": all_count
			}
		return notifications
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

""" updating notification in context """
def context_data(request):
	context = {}
	notifications_data = notifications(request)
	context.update(notifications_data)
	return context

################################################### users / customers #################################################
""" New Customers with no transactions """
@login_required(login_url='mophy:login')
@permission_required('view_customer', raise_exception=True)
def new_customers(request):
	try:
		context = context_data(request)
		new_customers = User.objects.filter(is_superuser=False).values().order_by("-id")
		new_customers_array = []
		for x in new_customers:
			if not Transaction_details.objects.filter(Q(payment_status=transaction['completed']) | Q(payment_status=transaction['pending_review']) | Q(payment_status=transaction['cancelled']), customer_id=x['customer_id']).exists():
				new_customers_array.append(x)		
		context.update(title="New Customers", user_list= data_to_None(new_customers_array))
		return render(request,'mophy/modules/users.html',context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

""" Get all Users / Customers """
@login_required(login_url='mophy:login')
@permission_required('view_customer', raise_exception=True)
def users(request):
	try:
		context = context_data(request)
		pageType = 'customer'
		changeValue = request.session.get('changeValue')
		csv_key = request.session.get('csv_key_'+pageType)
		csv_value = request.session.get('csv_value_'+pageType)
		csv_db_value = request.session.get('csv_db_value_'+pageType)
		if csv_key == None or csv_db_value == None or csv_key == 'null' or csv_db_value == 'null':
			data = list(User.objects.filter(is_superuser=False, is_admin=False).values().order_by('-id'))
		else:
			user_data = get_csv_user_data(csv_key, csv_db_value)
			data = user_data['data']
		if changeValue == None or changeValue == 1:
			request.session['csv_key_'+pageType] = None
			request.session['csv_value_'+pageType] = None
			request.session['csv_db_value_'+pageType] = None
			request.session['changeValue'] = 0	    
		else:
			pass		
		context.update(title="Customers" , user_list = data_to_None(data), csv_filter_list = CSV_CUSTOMER_FILTER_KEYS, filter_value =csv_key,  value=csv_value)
		return render(request, "mophy/modules/users.html",context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

""" User Detail """
@login_required(login_url='mophy:login')
@permission_required('view_customer', raise_exception=True)
def user_details(request,id):
	try:
		context = context_data(request)
		payid = None
		payto = None
		payment_tier_data = None
		value_tier_data = None
		#updating notification data if user user has viewed notification
		if is_obj_exists(notification, {'source_id':id}):
			update_model_obj(notification, {'source_id':id}, {'read':True})

		#fetching user details including address	
		if is_obj_exists(User, {'customer_id':id}):
			user_obj = User.objects.filter(customer_id=id).values()[0]
			context.update(user_obj = data_to_None([user_obj])[0])	
			if is_obj_exists(User_address, {'user_id':user_obj['id']}):
				address = User_address.objects.filter(user_id=user_obj['id']).values()
				context.update(address = data_to_None(address)[0])		

			#fetching zai payid and agreement details 	
			if is_obj_exists(zai_payid_details, {'user_id':user_obj['id']}):
				payid = zai_payid_details.objects.filter(user_id=user_obj['id']).values()
				context.update(payid = data_to_None(payid)[0])
			if is_obj_exists(zai_agreement_details, {'user_id':user_obj['id']}):
				payto = zai_agreement_details.objects.filter(user_id=user_obj['id']).values()
				context.update(payto = data_to_None(payto)[0])
		
			#fetching recipients list of user
			if is_obj_exists(Recipient, {'user_id':user_obj['id']}):
				recipient_count = Recipient.objects.filter(user_id= user_obj['id']).count()
				recipient_data = Recipient.objects.filter(user_id= user_obj['id']).values('id')
				if is_obj_exists(Recipient_bank_details, {'recipient_id__in':recipient_data}):
					bank_data = Recipient_bank_details.objects.filter(recipient_id__in=recipient_data).values('id','recipient_id','bank_name','account_name','account_number', 'recipient_id__email','recipient_id__first_name','recipient_id__middle_name','recipient_id__last_name','recipient_id__mobile','recipient_id__flat','recipient_id__building','recipient_id__street','recipient_id__postcode','recipient_id__city','recipient_id__state','recipient_id__country')
					context.update(recipients = data_to_None(bank_data), total_recipients = recipient_count)
				else:
					context.update(total_recipients = recipient_count)

			#fetching transactions of user
			if is_obj_exists(Transaction_details, {'customer_id':user_obj['customer_id']}):
				transaction_data = list(Transaction_details.objects.filter(customer_id = user_obj['customer_id']).values().order_by('-updated_at'))
				for i in list(transaction_data):
					i['date'] = str(i['date'])
					i['amount'] = comma_value(i['amount'])
					i['receive_amount'] = comma_value(i['receive_amount'])
					i['exchange_rate'] = comma_value(i['exchange_rate'])
					i = {key: None if str(value).strip() == '' or value == None else value for key, value in i.items()}
				transaction_count = Transaction_details.objects.filter(customer_id = user_obj['customer_id']).count()
				aud_amount = Transaction_details.objects.filter(Q(payment_status=transaction['pending_review']) | Q(payment_status=transaction['completed']),send_currency="AUD", customer_id=user_obj['customer_id']).aggregate(total=Sum('amount'))
				nzd_amount = Transaction_details.objects.filter(Q(payment_status=transaction['pending_review']) | Q(payment_status=transaction['completed']),send_currency="NZD", customer_id=user_obj['customer_id']).aggregate(total=Sum('amount'))
				context.update(transaction_array=transaction_data, total_transactions = transaction_count, aud_amount=comma_value(aud_amount['total']), nzd_amount=comma_value(nzd_amount['total']))

		#get old tier values in context
		if is_obj_exists(Tiers, {'customer_id':id}):
			payment_tier_data = Tiers.objects.filter(customer_id=id, type='payment_per_annum').values('old_tier','updated_at').last()
			value_tier_data = Tiers.objects.filter(customer_id=id, type='value_per_annum').values('old_tier','updated_at').last()
			context.update(old_payment_tier=payment_tier_data, old_value_tier=value_tier_data)
		#update tiers list and old values in context
		context.update(payment_per_annum_list=ADMIN_PAYMENT_PER_ANNUM_LIST, value_per_annum_list=ADMIN_VALUE_PER_ANNUM_LIST,
				old_payment_tier=payment_tier_data, old_value_tier=value_tier_data, documents_list=ADMIN_DOCUMENTS_STATUS_LIST
			)
		return render(request,"mophy/modules/user-details.html",context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		CreateErrorFile(file_content)
		return False

""" Update Payment and Value Per Annum """
@login_required(login_url='mophy:login')
@permission_required('edit_customer', raise_exception=True)
def update_tier(request):
	try:
		if request.method == 'POST':
			message = 'New Tier value has been updated successfully.'
			customer_id = request.POST.get('customer_id')
			old_value = request.POST.get('old_value')
			new_value = request.POST.get('new_value')
			type = request.POST.get('type')
			documents_value = request.POST.get('documents_value')

			if str(documents_value).lower() != 'approved':
				return JsonResponse({'success':False, 'message':'Kindly review and approve the documents before updating Tier status.'})
			if not User.objects.filter(customer_id=customer_id).exists():
				return JsonResponse({'success':False})
			if type == 'payment_per_annum':
				User.objects.filter(customer_id=customer_id).update(payment_per_annum=new_value)
				message = 'Payment per annum value has been updated successfully.'
			elif type == 'value_per_annum':
				User.objects.filter(customer_id=customer_id).update(value_per_annum=new_value)
				message = 'Value per annum value has been updated successfully.'
			obj = create_tier(customer_id, old_value, new_value, type)
			if obj != True:
				return JsonResponse({'success':False, 'message':'Something went wrong. Please Try again later'})
			return JsonResponse({'success':True, 'message':message})
		else:
			return redirect('mophy:users')
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return JsonResponse({'success':False, 'message':'Something went wrong. Please Try again later'})
	
""" Disable User """
@login_required(login_url='mophy:login')
@permission_required('delete_customer', raise_exception=True)
def delete_user(request,id):
	try:
		if request.method == 'POST':
			if User.objects.filter(customer_id=id).exists():
				User.objects.filter(customer_id=id).update(delete=True, is_active=False)
				messages.success(request, "Customer disabled successfully") 
				return JsonResponse({'success':True})
			else:
				return JsonResponse({'success':False})
		return redirect('mophy:users')
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

""" Enable User """
@login_required(login_url='mophy:login')
@permission_required('delete_customer', raise_exception=True)
def enable_user(request,id):
	try:
		if request.method == 'POST':
			if User.objects.filter(customer_id=id).exists():
				User.objects.filter(customer_id=id).update(delete=False, is_active=True)
				messages.success(request, "Customer enabled successfully") 
				return JsonResponse({'success':True})
			else:
				return JsonResponse({'success':False})
		return redirect('mophy:users')
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

""" Update Documents Status """
@login_required(login_url='mophy:login')
@permission_required('edit_customer', raise_exception=True)
def update_documents_status(request):
	try:
		status = None
		if request.method == 'POST':
			message = 'Status has been updated successfully.'
			customer_id = request.POST.get('customer_id')
			status = request.POST.get('status')
			
			if not User.objects.filter(customer_id=customer_id).exists():
				return JsonResponse({'success':False})
			if status:
				User.objects.filter(customer_id=customer_id).update(documents=str(status).lower())
				return JsonResponse({'success':True, 'message':message})
			return JsonResponse({'success':False})
		else:
			return redirect('mophy:users')
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return JsonResponse({'success':False, 'message':'Something went wrong. Please Try again later'})

############################################### Admin Users #############################################
""" Admin Users """
@login_required(login_url='mophy:login')
@permission_required('view_admin_user', raise_exception=True)
def admin_users(request):
	try:
		context={}
		notifications_data = notifications(request)
		context.update(notifications_data)
		users= User.objects.filter(is_superuser=True, is_admin=False).values().order_by('-id')
		for x in users:
			if is_obj_exists(admin_roles, {'user_id':x['id']}):
				role_data = admin_roles.objects.filter(user_id=x['id']).values('role_id','role_id__name')
				x.update(role = role_data[0]['role_id__name'])
			else:
				x.update(role = None)	
			if x['First_name'] is not None and x['Last_name'] is not None:
				x.update(name = str(x['First_name']+" "+str(x['Last_name'])))
			elif x['First_name'] is not None:
				x.update(name = str(x['First_name']))
			else:
				x.update(name = None)
			x = items_to_none(x)
			# x = {key: None if str(value).strip() == '' else str(value) for key, value in x.items()}
		context.update(user_list = users)
		return render(request, "mophy/modules/admin_users.html",context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

""" Disable Admin User """
@login_required(login_url='mophy:login')
@permission_required('delete_admin_user', raise_exception=True)
def delete_admin_user(request,id):
	try:
		context = {}
		notifications_data = notifications(request)
		context.update(notifications_data)
		if is_obj_exists(User, {'id':id}):
			User.objects.filter(id=id).update(delete=True)
		all_sessions = Session.objects.filter(expire_date__gte=timezone.now())
		if all_sessions:
			for i in list(all_sessions):
				uid = i.get_decoded().get('_auth_user_id')
				if str(uid) == str(id):
					i.delete()
			return JsonResponse({'success':True})
		else:
			return JsonResponse({'success':False})
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

""" Enable Admin User """
@login_required(login_url='mophy:login')
@permission_required('delete_customer', raise_exception=True)
def enable_admin_user(request,id):
	try:
		if request.method == 'POST':
			if User.objects.filter(id=id).exists():
				User.objects.filter(id=id).update(delete=False)
				messages.success(request, "Customer enabled successfully") 
				return JsonResponse({'success':True})
			else:
				return JsonResponse({'success':False})
		return redirect('mophy:users')
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
################################################### Transactions #################################################
""" All Transactions with and without filter """
@login_required(login_url='mophy:login')
@permission_required('view_transaction', raise_exception=True)
def transactions(request):
	try:
		context = context_data(request)
		array = []
		pageType = 'transaction'
		changeValue = request.session.get('changeValue')
		csv_key = request.session.get('csv_key_'+pageType)
		csv_value = request.session.get('csv_value_'+pageType)
		csv_db_value = request.session.get('csv_db_value_'+pageType)
		if csv_key != None and csv_db_value != None and csv_key != 'null' and csv_db_value != 'null':
			trans_data = get_csv_transaction_data(csv_key, csv_db_value)
			transaction_data = trans_data['data']
		else:
			transaction_data = Transaction_details.objects.all().order_by('-updated_at')
		if changeValue == None or changeValue == 1:
			request.session['csv_key_'+pageType] = None
			request.session['csv_value_'+pageType] = None
			request.session['csv_db_value_'+pageType] = None
			request.session['changeValue'] = 0	    
		else:
			pass	
		if transaction_data:
			transaction_serializer = Transaction_details_web_Serializer(transaction_data, many=True)
			for i in list(transaction_serializer.data):
				i = dict(i)
				i['amount'] = comma_value(i['amount'])
				i['receive_amount'] = comma_value(i['receive_amount'])
				i['exchange_rate'] = comma_value(i['exchange_rate'])
				if str(i['total_amount']) == "0.0000" or i['total_amount'] == None or str(i['total_amount']).strip() == '':
					i['total_amount'] = comma_value(i['amount'])
				else:
					i['total_amount'] = comma_value(i['total_amount'])
				i['discount_amount'] = comma_value(i['discount_amount'])
				array.append(i)
		context.update(transaction=data_to_None(array), title= "Transaction History", csv_filter_list = CSV_TRANSACTION_FILTER_KEYS, filter_value =csv_key ,  value=csv_value)
		return render(request,'mophy/transactions.html',context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

""" Transaction Details """
@login_required(login_url='mophy:login')
@permission_required('view_transaction', raise_exception=True)
def transactions_details(request, id):
	try:
		payment_reason = None
		payment_status = None
		payment_status_list = []
		#updationg notification data
		if notification.objects.filter(source_id=id).exists():
			notification.objects.filter(source_id=id).update(read=True)
		context = context_data(request)

		if not Transaction_details.objects.filter(id=id).exists():
			return render(request,'mophy/transactions.html',context)	

		#payment status list from settings
		for key, value in transaction.items():
			transaction_obj = {'key': value,'value': value	}
			payment_status_list.append(transaction_obj)
		payment_status_list.insert(0, {'key':"Select Payment status", "value":None})
		
		#adding comma and decimals in amounts
		obj = get_object_or_404(Transaction_details, id=id)
		obj.amount = comma_value(obj.amount)
		obj.receive_amount = comma_value(obj.receive_amount)
		obj.exchange_rate = comma_value(obj.exchange_rate)
		obj.total_amount = comma_value(obj.total_amount)
		obj.discount_amount = comma_value(obj.discount_amount)
		if obj.send_method == "zai_payid_per_user":
			obj.send_method = "PayID Per User"
		elif obj.send_method == "zai_payto_agreement":
			obj.send_method = "PayTo Agreement"
		else:
			obj.send_method = str(obj.send_method).replace("_"," ").title()
		context.update(data = obj, payment_status_list=payment_status_list, title = "all_transactions")

		#fetching user payId and payTo agreement details
		if User.objects.filter(customer_id=obj.customer_id).exists():
			customer = get_object_or_404(User, customer_id = obj.customer_id)
			payid= None
			payto = None
			address = None
			if zai_payid_details.objects.filter(user_id=customer.id).exists():
				payid = zai_payid_details.objects.filter(user_id=customer.id)[0]
			if zai_agreement_details.objects.filter(user_id=customer.id).exists():
				payto = zai_agreement_details.objects.filter(user_id=customer.id)[0]
			if User_address.objects.filter(user_id=customer.id).exists():
				address = User_address.objects.filter(user_id=customer.id)[0]
			context.update(address=address, customer=customer, payto=payto, payid=payid)
			# fetching recipient details and bank details 
			if obj.recipient:
				if Recipient.objects.filter(id=obj.recipient).exists():
					recipient =  Recipient.objects.filter(id=obj.recipient)[0]
					context.update(recipient=recipient)
				if Recipient_bank_details.objects.filter(recipient_id=obj.recipient).exists():
					bank = Recipient_bank_details.objects.filter(recipient_id=obj.recipient)[0]
					context.update(bank=bank)
						
		#updating payment status and reason 
		if request.method == 'POST':
			payment_status = request.POST.get('payment_status')
			payment_reason = request.POST.get('payment_reason')
			if str(payment_status) != "None":
				# # ==== updating transaction status in FN
				# if str(payment_status).lower() == "cancelled":
				# 	status = "cancelled"
				# 	fn_transaction_update(transaction_id=id, status=status)
				# else:
				# 	status = "approved"
				# 	fn_transaction_update(transaction_id=id, status=status)

				# updating new and old payment status in payment status table
				Transaction_details.objects.filter(id=id).update(payment_status=payment_status, payment_status_reason=payment_reason)
				status_data = Transaction_details.objects.filter(id=id).values()

				#if payment status is completed then sending sms and email to customer and recipient
				if not payment_status_details.objects.filter(status=payment_status,transaction_id=status_data[0]['transaction_id']).exists() and status_data[0]['payment_status'] == transaction['completed']:
					sending_sms_email_to_customer_recipient(status_data=status_data)
					payment_status_details.objects.create(status_reason=payment_reason,status=payment_status,transaction_id=status_data[0]['transaction_id'])
					return redirect('mophy:transactions-details', id=id)
			return redirect('mophy:transactions-details', id=id)
		else:
			return render(request,'mophy/transactions-details.html',context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

""" Pending Payment Transactions """
@login_required(login_url='mophy:login')
@permission_required('view_transaction', raise_exception=True)
def pending_payment_transactions_view(request):
	try:
		context = context_data(request)
		array = []
		transaction_data = Transaction_details.objects.filter(payment_status=transaction['pending_payment']).order_by('-updated_at')
		if transaction_data:
			transaction_serializer = Transaction_details_web_Serializer(transaction_data, many=True)
			for i in list(transaction_serializer.data):
				i = dict(i)
				i['amount'] = comma_value(i['amount'])
				i['receive_amount'] = comma_value(i['receive_amount'])
				i['exchange_rate'] = comma_value(i['exchange_rate'])
				i['total_amount'] = comma_value(i['total_amount'])
				i['discount_amount'] = comma_value(i['discount_amount'])
				array.append(i)
		context.update(transaction=data_to_None(array), title= "Pending Payment Transactions")
		return render(request,'mophy/transactions.html',context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
""" Incomplete Transactions """
@login_required(login_url='mophy:login')
@permission_required('view_transaction', raise_exception=True)
def incomplete_transactions(request):
	try:
		context = context_data(request)
		array = []
		transaction_data = Transaction_details.objects.filter(payment_status=transaction['incomplete']).order_by('-updated_at')
		if transaction_data:
			transaction_serializer = Transaction_details_web_Serializer(transaction_data, many=True)
			for i in list(transaction_serializer.data):
				i = dict(i)
				i['amount'] = comma_value(i['amount'])
				i['receive_amount'] = comma_value(i['receive_amount'])
				i['exchange_rate'] = comma_value(i['exchange_rate'])
				i['total_amount'] = comma_value(i['total_amount'])
				i['discount_amount'] = comma_value(i['discount_amount'])
				array.append(i)
		context.update(transaction=data_to_None(array), title= "Incomplete Transactions")
		return render(request,'mophy/transactions.html',context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

""" Pending Payout Transactions (Pending Review and Processing) """
@login_required(login_url='mophy:login')
@permission_required('view_transaction', raise_exception=True)
def pending_review_processing_transactions(request):
	try:
		context = context_data(request)
		array = []
		transaction_data = Transaction_details.objects.filter(payment_status=transaction['pending_review']).order_by('-updated_at')
		transaction_serializer = Transaction_details_web_Serializer(transaction_data, many=True)
		if transaction_data:
			transaction_serializer = Transaction_details_web_Serializer(transaction_data, many=True)
			for i in list(transaction_serializer.data):
				i = dict(i)
				i['amount'] = comma_value(i['amount'])
				i['receive_amount'] = comma_value(i['receive_amount'])
				i['exchange_rate'] = comma_value(i['exchange_rate'])
				i['total_amount'] = comma_value(i['total_amount'])
				i['discount_amount'] = comma_value(i['discount_amount'])
				array.append(i)
		context.update(transaction=data_to_None(array), title= "Pending Review and Processing Transactions")
		return render(request,'mophy/transactions.html',context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

""" FN Approved Transactions """
@login_required(login_url='mophy:login')
@permission_required('view_transaction', raise_exception=True)
def approved_transactions(request):
	try:
		context = context_data(request)
		array = []
		transaction_data = Transaction_details.objects.filter(tm_status=fn_approved).order_by('-updated_at')
		if transaction_data:
			transaction_serializer = Transaction_details_web_Serializer(transaction_data, many=True)
			for i in list(transaction_serializer.data):
				i = dict(i)
				i['amount'] = comma_value(i['amount'])
				i['receive_amount'] = comma_value(i['receive_amount'])
				i['exchange_rate'] = comma_value(i['exchange_rate'])
				i['total_amount'] = comma_value(i['total_amount'])
				i['discount_amount'] = comma_value(i['discount_amount'])
				array.append(i)
		context.update(transaction=data_to_None(array), title= "FN Approved Transactions")
		return render(request,'mophy/transactions.html',context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

""" FN Queued Transactions """
@login_required(login_url='mophy:login')
@permission_required('view_transaction', raise_exception=True)
def queued_transactions(request):
	try:
		context = context_data(request)
		array = []
		transaction_data = Transaction_details.objects.filter(tm_status=fn_queued).order_by('-updated_at')
		if transaction_data:
			transaction_serializer = Transaction_details_web_Serializer(transaction_data, many=True)
			for i in list(transaction_serializer.data):
				i = dict(i)
				i['amount'] = comma_value(i['amount'])
				i['receive_amount'] = comma_value(i['receive_amount'])
				i['exchange_rate'] = comma_value(i['exchange_rate'])
				i['total_amount'] = comma_value(i['total_amount'])
				i['discount_amount'] = comma_value(i['discount_amount'])
				array.append(i)
		context.update(transaction=data_to_None(array), title= "FN Queued Transactions")
		return render(request,'mophy/transactions.html',context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

""" Cancelled Transactions """
@login_required(login_url='mophy:login')
@permission_required('view_transaction', raise_exception=True)
def cancelled_transactions(request):
	try:
		context = context_data(request)
		array = []
		transaction_data = Transaction_details.objects.filter(payment_status=transaction['cancelled']).order_by('-updated_at')
		if transaction_data:
			transaction_serializer = Transaction_details_web_Serializer(transaction_data, many=True)
			for i in list(transaction_serializer.data):
				i = dict(i)
				i['amount'] = comma_value(i['amount'])
				i['receive_amount'] = comma_value(i['receive_amount'])
				i['exchange_rate'] = comma_value(i['exchange_rate'])
				i['total_amount'] = comma_value(i['total_amount'])
				i['discount_amount'] = comma_value(i['discount_amount'])
				array.append(i)
		context.update(transaction=data_to_None(array), title= "Cancelled Transactions")
		return render(request,'mophy/transactions.html',context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

################################################### Zai #################################################
""" Zai Home Page """
@login_required(login_url='mophy:login')
@permission_required('view_zai', raise_exception=True)
def zai_home_page(request):	
	try:
		context = context_data(request)	
		context2 = {}
		graph_time = "1"
		today = get_current_date()

		#default zai remitassure id to receive payins
		zai_user_id = settings.ZAI_REMIT_USER_ID

		#fetching withdraw data history
		withdraw_data = withdraw_zai_funds.objects.all().values().order_by('-id')	
		withdraw_data = data_to_none_str(withdraw_data)

		#get wallet balance and email
		wallet = get_wallet_balance(zai_user_id=zai_user_id, request=request)

		#all remitassure users account to receive payins
		bank_list = list(zai_admin_users.objects.all().values())
		if not bank_list:
			bank_list = list(settings.ZAI_ADMIN_USERS)
		
		#inserting default bank at 0 index
		for s in bank_list:
			if str(s['zai_user_id']) == str(zai_user_id):
				s_index = bank_list.index(s)
				bank_list.pop(s_index)
				bank_list.insert(0, {'bank_name': s['bank_name'], 'zai_user_id':s['zai_user_id'], 'zai_email':s['zai_email']})

		#zai graph data
		pay_data = get_zai_payin_payout(graph_time, zai_user_id, request)
		context.update(data=withdraw_data, zai_email=wallet['zai_email'], wallet_balance=wallet['wallet_balance'], bank_list=bank_list, payin_data= pay_data['payin_data'], payin=pay_data['payin'], payout=pay_data['payout'], pending_payout=pay_data['pending_payout'])
		context2.update(payout_data=pay_data['payout_data'], payout_volume=pay_data['payout_volume'] ,payin_volume=pay_data['payin_volume'] ,payin_data= pay_data['payin_data'], payin=pay_data['payin'], payout=pay_data['payout'], pending_payout=pay_data['pending_payout'])
		context.update(context2_json = json.dumps(context2))

		if request.method == 'POST':		
			zai_user_id = request.POST.get('zai_user_id')
			graph_time = request.POST.get('graph_time')	
			pay_data = get_zai_payin_payout(graph_time, zai_user_id, request)
			return JsonResponse({'success':True, 'zai_email':wallet['zai_email'], 'wallet_balance':wallet['wallet_balance'], 'payout_volume':pay_data['payout_volume'],'payout_data':pay_data['payout_data'],'payin':pay_data['payin'], 'payout':pay_data['payout'],'pending_payout':pay_data['pending_payout'],'payin_volume':pay_data['payin_volume'], 'payin_data': pay_data['payin_data']})
		else:
			return render(request,'mophy/zai.html', context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

""" Get zai wallet balance and email of user """
@login_required(login_url='mophy:login')
@permission_required('view_zai', raise_exception=True)
def zai_wallet_of_user(request):	
	try:
		if request.method == "POST":
			zai_user_id = request.POST.get('zai_user_id')
			if zai_user_id:
				wallet = get_wallet_balance(zai_user_id=zai_user_id, request=request)
				return JsonResponse({'success':True, 'email':wallet['zai_email'], 'balance':wallet['wallet_balance']})
		return JsonResponse({'success':False})
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

""" Withdraw Zai Funds """
@login_required(login_url='mophy:login')
@permission_required('view_zai', raise_exception=True)
def withdraw_funds_from_zai(request):	
	try:
		context = context_data(request)	
		context2 = {}
		
		if request.method == 'POST':		
			zai_user_id = request.POST.get('zai_user_id')
			amount = request.POST.get('amount')	

			#get wallet balance
			if zai_user_id and amount:
				wallet_data =  get_wallet_balance(zai_user_id=zai_user_id, request=request)	
				if float(replace_comma(amount)) > float(replace_comma(wallet_data['wallet_balance'])):
					return JsonResponse({'success':False,'message':"Insufficient Balance"})
				
				#withdraw amount
				withdraw_data = withdraw_amount(zai_user_id, amount, request, wallet_data['wallet_id'], wallet_data['wallet_balance'])
				if 'errors' in withdraw_data['response']:
					return JsonResponse({'success':False,'message':withdraw_data['response']['errors']	})		
				return JsonResponse({'success':True,'type':"completed",'message':"Funds withdrawn successfully.",'wallet_balance': withdraw_data['new_balance'],'zai_email':wallet_data['zai_email']})
		return redirect('zai')
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

""" All WidophRemit Zai Wallets """
@login_required(login_url='mophy:login')
@permission_required('view_zai', raise_exception=True)
def my_wallets(request):
	try:
		dict = {}
		list = []
		context = context_data(request)
		users = zai_admin_users.objects.all().values('id','bank_name','zai_user_id','zai_email')
		if not users:
			users = settings.ZAI_ADMIN_USERS
		for i in users:
			data =  get_wallet_balance(i['zai_user_id'], request)
			dict = {'wallet_balance':data['wallet_balance'], 'zai_user_id':i['zai_user_id'],'zai_email':data['zai_email'],'bank_name':i['bank_name']}
			list.append(dict)
		context.update(data=list)
		return render(request,'mophy/my_wallets.html', context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

""" WidophRemit Wallet Transfer """
@login_required(login_url='mophy:login')
def zai_transfer(request, id):
	try:
		dict = {}
		list = []
		context = context_data(request)
		source_id = id		
		s_balance =  get_wallet_balance(source_id, request)
		users = zai_admin_users.objects.all().values()
		if not users:
			users = settings.ZAI_ADMIN_USERS
		for i in users:
			if str(i['zai_user_id']) == str(source_id):
				context.update(source_bank = i['bank_name'])
			data = get_wallet_balance(i['zai_user_id'], request)
			dict = {'wallet_balance':data['wallet_balance'], 'zai_user_id':i['zai_user_id'],'zai_email':data['zai_email'],'bank_name':i['bank_name']}
			list.append(dict)
		context.update(data=list, source_id=source_id, source_wallet_balance=s_balance['wallet_balance'],source_zai_email=s_balance['zai_email'])
		
		if request.method == 'POST':		
			destination_id = request.POST.get('zai_user_id')		
			amount = request.POST.get('amount')		

			if amount and destination_id:
				if float(replace_comma(amount)) > float(replace_comma(s_balance['wallet_balance'])):
					return JsonResponse({'success':False, 'message':"Insufficient Balance"})
				
				#transferring funds from one wallet to another
				amount_response = zai_wallet_transfer(source_id, destination_id, amount, request)
				if amount_response['code'] == 400:
					return JsonResponse({'success':False, 'message':amount_response['message']})
			
			if destination_id:
				d_balance = get_wallet_balance(destination_id, request)

			if amount:
				return JsonResponse({'success':True, 'type':"completed", 'message':"Funds are transferred from source walllet to destination wallet.",'source_wallet_balance':comma_value(amount_response['new_balance']),'source_zai_email':amount_response['zai_email'],'destination_wallet_balance':d_balance['wallet_balance'],'destination_zai_email':d_balance['zai_email']})
			return JsonResponse({'success':True,'source_wallet_balance':s_balance['wallet_balance'],'source_zai_email':s_balance['zai_email'],'destination_wallet_balance':d_balance['wallet_balance'],'destination_zai_email':d_balance['zai_email']})
		return render(request,'mophy/zai_transfer.html', context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
################################################### Transaction Monitoring #################################################
""" Transaction monitoring page """
@login_required(login_url='mophy:login')
@permission_required('view_transaction_monitoring', raise_exception=True)
def transaction_monitoring(request):
	try:
		context = context_data(request)
		date = None
		tm_status = None
		corridor = None
		send_currency = None
		receive_currency = None
		payment_status_list = [{"option":"Pending Payment", "value":"Pending Payment"}, {"option":"Completed", "value":"completed"}]
		tm_status_list = [{"option":"Approved", "value":"approved"}, {"option":"Cancelled", "value":"cancelled"}, {"option":"Queued", "value":"queued"}	]
		corridors_list = [{"country":"All corridors", "currency":"all"},{"country":"Kenya", "currency":"KES"}, {"country":"Ghana", "currency":"GHS"},{"country":"Philippines", "currency":"PHP"}, {"country":"Nigeria (NGN)", "currency":"NGN"},{"country":"Nigeria (USD)", "currency":"USD"}, {"country":"Vietnam", "currency":"VND"}, {"country":"Thailand", "currency":"THB"}]
		send_currency_list = [{"country":"Australia", "currency":"AUD"}, {"country":"New Zealand", "currency":"NZD"}]
		receive_currency_list = [{"country":"Kenya", "currency":"KES"}, {"country":"Ghana", "currency":"GHS"},{"country":"Philippines", "currency":"PHP"}, {"country":"Nigeria", "currency":"NGN"},{"country":"Nigeria", "currency":"USD"}, {"country":"Vietnam", "currency":"VND"}, {"country":"Thailand", "currency":"THB"}]	
		
		if request.method == 'POST':
			send_currency = request.POST.get('send_currency')
			receive_currency = request.POST.get('receive_currency')
			date = request.POST.get('date')
			tm_status = request.POST.get('tm_status')
			corridor = request.POST.get('corridor')

			if send_currency is not None:
				for s in send_currency_list:
					if s['currency'] == str(send_currency):
						s_index = send_currency_list.index(s)
						send_currency_list.pop(s_index)
						send_currency_list.insert(0, {'country': s['country'], 'currency':s['currency']})
			
			if receive_currency is not None:	
				for r in receive_currency_list:
					if r['currency'] == str(receive_currency):
						r_index = receive_currency_list.index(r)
						receive_currency_list.pop(r_index)
						receive_currency_list.insert(0, {'country': r['country'], 'currency':r['currency']})
			
			if corridor is not None:
				for c in corridors_list:
					if c['currency'] == str(corridor):
						c_index = corridors_list.index(c)
						corridors_list.pop(c_index)
						corridors_list.insert(0, {'country': c['country'], 'currency':c['currency']})

			if tm_status is not None:
				for t in tm_status_list:
					if t['value'] == str(tm_status):
						t_index = tm_status_list.index(t)
						tm_status_list.pop(t_index)
						tm_status_list.insert(0, {'option': t['option'], 'value':t['value']})

		risk_group_transactions = risk_group_trasnactions_transaction_monitoring(send_currency, receive_currency)
		context.update(risk_group_transactions)
		dict={
			"all_transactions": Transaction_details.objects.all().count(),
			"total_pending_transactions":Transaction_details.objects.filter(payment_status=transaction['pending_payment']).count(),
			"approved_transactions": Transaction_details.objects.filter(tm_status=fn_approved).count(), 
			"cancelled_transactions": Transaction_details.objects.filter(payment_status=transaction['cancelled']).count(),
			"queue_transactions":  Transaction_details.objects.filter(tm_status=fn_queued).count(), 
			}
		
		pending_transactions = pending_payments_transaction_monitoring(corridor, tm_status)
		context.update(pending_transactions= pending_transactions)
		
		#updating filter lists
		if send_currency is None:
			send_currency_list.insert(0, {'country':'Choose a currency', 'currency':None})
		if receive_currency is None:
			receive_currency_list.insert(0, {'country':'Choose a currency', 'currency':None})
		if tm_status is None:
			tm_status_list.insert(0, {'option':'Choose status', 'value':None})
		if corridor is None:
			corridors_list.insert(0, {'country':'Choose corridor', 'currency':None})
		context.update(dict)
		context.update(send_currency_list=send_currency_list, receive_currency_list=receive_currency_list, payment_status_list=payment_status_list, tm_status_list=tm_status_list, corridors_list= corridors_list)
		return render(request, "mophy/modules/transaction_monitoring.html",context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
################################################### Customer Referrals #################################################

""" Referrals Page """
@login_required(login_url='mophy:login')
@permission_required('view_loyality_program', raise_exception=True)
def customer_referrals(request):
	try:
		context = context_data(request)	
		meta = referral_meta.objects.all().values('id','transaction_id','user_id','user_id__customer_id','referred_to','referral_id__referral_type_id').order_by('-id')
		for x in meta:
			invites = referral_meta.objects.filter(user_id=x['user_id']).values('referred_to')
			total_invites = 0
			unclaimed_rewards_count = 0
			for i in invites:
				if str(i['referred_to']) != '' and i['referred_to'] != None :
					total_invites += 1
			claimed_rewards = referral_meta.objects.filter(user_id = x['user_id'], is_used=True).count()
			user = get_object_or_404(User, id=x['user_id'])
			unclaimed_data = unclaimed_rewards("AUD", user, x['user_id'])
			if unclaimed_data:
				unclaimed_rewards_count = len(unclaimed_data)
			total_rewards = claimed_rewards+unclaimed_rewards_count

			x.update(total_invites=total_invites, total_rewards = total_rewards, claimed_rewards=claimed_rewards, unclaimed_rewards=unclaimed_rewards_count)
		
		unique_user_ids = set()
		filtered_data = []
		for entry in meta:
			user_id = entry['user_id']
			if user_id not in unique_user_ids:
				unique_user_ids.add(user_id)
				filtered_data.append(entry)
		context.update(data=filtered_data)
		return render(request,'mophy/customer_referrals.html', context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
""" User referral rewards details """
@login_required(login_url='mophy:login')
@permission_required('view_loyality_program', raise_exception=True)
def referral_detail(request, id): #id is user_id
	context = context_data(request)
	try:
		user =  get_object_or_404(User, id=id)
		filter_currency = "AUD"

		#get claimed rewards
		claimed_data = list(referral_meta.objects.filter(user_id=id, is_used=True).values('id','referral_id__currency','referral_id__referral_type_id__type','referral_id__name','transaction_id','claimed_date','referral_id__referred_by_amount','discount','referred_by').order_by('-id'))

		#get unclaimed rewards
		unclaimed_data = unclaimed_rewards(filter_currency, user, id)
		#updating information of customer who referred this customer
		if referral_meta.objects.filter(referred_to=id).exists():
			referred_by_data = list(referral_meta.objects.filter(referred_to=id).values('user_id'))		
			context.update(referred_by = get_object_or_404(User, id=referred_by_data[0]['user_id']))
		context.update(claimed_data = data_to_none_str(claimed_data), unclaimed_data=unclaimed_data, user=user)
		return render(request,'mophy/referral_detail.html', context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False


################################################### KYC / Veriff #################################################
@login_required(login_url='mophy:login')
@permission_required('view_veriff', raise_exception=True)
def veriff(request):
	try:
		media_data = None
		context = context_data(request) 
		data = list(Veriff.objects.all().values().order_by('-id'))
		if data:
			for item in data:
				#get veriff media
				if is_obj_exists(Veriff_media, {'customer_id':item['customer_id']}):
					media_data = Veriff_media.objects.filter(customer_id=item['customer_id']).values('path','name','type')
					print(media_data)
					item.update(media_data=json.dumps(list(media_data)))
				for key, value in item.items():
					if key == 'status':
						item[key] = str(value).replace("_"," ")
					if value == '':
						item[key] = None
			context.update(data=data)
		if ADMIN_VERIFF_STATUS_LIST:
			context.update(veriff_status_list=ADMIN_VERIFF_STATUS_LIST)
		return render(request, "mophy/modules/veriff.html", context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False


""" Update Veriff Status """
@login_required(login_url='mophy:login')
@permission_required('edit_veriff', raise_exception=True)
def update_veriff_status(request):
	try:
		if request.method == 'POST':
			message = 'Veriff status has been updated successfully.'
			customer_id = request.POST.get('customer_id')
			veriff_status = request.POST.get('status_value')
			print(veriff_status, "veriff status = = == = = = ")
			if not User.objects.filter(customer_id=customer_id).exists():
				return JsonResponse({'success':False})
			User.objects.filter(customer_id=customer_id).update(is_digital_Id_verified=str(veriff_status).lower())
			if Veriff.objects.filter(customer_id=customer_id).exists():
				Veriff.objects.filter(customer_id=customer_id).update(status=str(veriff_status).lower())
			return JsonResponse({'success':True, 'message':message})
		else:
			return redirect('mophy:veriff')
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return JsonResponse({'success':False, 'message':'Something went wrong. Please Try again later'})
	
################################################### Forex #################################################
""" Forex Page """
@login_required(login_url='mophy:login')
@permission_required('view_forex', raise_exception=True)
def forex_details(request):
	try:
		context = context_data(request)
		context2 = {}
		context.update(exist = False)
		context2.update(exist = False)
		context.update(payin_list = SEND_CURRENCY_LIST, payout_list = RECEIVE_CURRENCY_LIST)
		if request.method == 'POST':
			source_currency = request.POST.get('source_currency')
			destination_currency = request.POST.get('destination_currency')
			rate = request.POST.get('rate')
			markup = request.POST.get('markup')
			source = request.POST.get('source')

			if source_currency and destination_currency and rate and markup:
				if forex.objects.filter(source_currency=source_currency, destination_currency=destination_currency).exists():
					context.update(exist = True)
				else:
					new_forex = forex(source_currency=source_currency,destination_currency=destination_currency,
						rate=rate, markup=markup, source="manual", is_enabled=True)
					new_forex.save()
			else:
				messages.warning(request, 'Please select source and destination currency.')
			return redirect('mophy:forex-details')
		table_data = list(forex.objects.all().values('id','source_currency','destination_currency','rate','markup','source','is_enabled'))
		for x in table_data:
			x['rate'] = comma_value(x['rate'])
		context.update(table_data = table_data)
		context2.update(table_data = table_data)
		json_context = json.dumps(context2)
		context.update(json_context = json_context)
		return render(request,'mophy/forex.html', context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
""" Edit Forex """
@login_required(login_url='mophy:login')
@permission_required('edit_forex', raise_exception=True)
def edit_forex(request):
	try:
		context = {}
		notifications_data = notifications(request)
		context.update(notifications_data)
		if request.method == 'POST':
			id = request.POST.get('row-id')
			markup = request.POST.get('markup')
			rate = request.POST.get('rate')  
			rate = str(rate).replace(",","").strip()
			markup = str(markup).replace(",","").strip()
			forex.objects.filter(id=id).update(markup=markup, rate=rate )
			return redirect('mophy:forex-details')
		else:
			return redirect('mophy:forex-details')
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
""" add forex currency data """
@login_required(login_url='mophy:login')
@permission_required('add_forex', raise_exception=True)
def add_forex(request):
	try:
		context = {}
		if request.method == 'POST':
			source_currency = request.POST.get('source_currency')
			destination_currency = request.POST.get('destination_currency')
			rate = request.POST.get('rate')
			markup = request.POST.get('markup')
			source = request.POST.get('source')
			is_enabled = request.POST.get('is_enabled') == 'on'
			rate =  str(rate).replace(",","").strip()
			markup =  str(markup).replace(",","").strip()
			if forex.objects.filter(source_currency=source_currency, destination_currency=destination_currency).exists():
				return redirect('mophy:forex-details')
				
			if not forex.objects.filter(source_currency=source_currency, destination_currency=destination_currency, source=source, is_enabled=True).exists():
				if forex.objects.filter(source_currency=source_currency, destination_currency=destination_currency, source='manual', is_enabled=True).exists():
					forex.objects.filter(source_currency=source_currency, destination_currency=destination_currency, source='manual',is_enabled=True).update(is_enabled=False)
			new_forex = forex(
				source_currency=source_currency,
				destination_currency=destination_currency,
				rate=rate,
				markup=markup,
				source=source,
				is_enabled=is_enabled
			)
			new_forex.save()
			return redirect('mophy:forex-details')
		return redirect('mophy:forex-details')
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
""" delete forex """
@login_required(login_url='mophy:login')
@permission_required('delete_forex', raise_exception=True)
def delete_forex(request, id):
	try:
		forex_instance = get_object_or_404(forex, id=id)
		forex_instance.delete()
		messages.success(request, 'Forex data deleted successfully.')
		return redirect('mophy:forex-details')
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False


#updating fraud.net status
def fn_transaction_update(transaction_id, status):
		url = settings.SANDBOX_URL
		payload = json.dumps({
		"order_id": str(transaction_id),
		"status": status
		})
		headers = {'Authorization': 'Basic '+settings.FRAUD_TOKEN,'Content-Type': 'application/json'}
		response = requests.request("PATCH", url, headers=headers, data=payload)
		return response



def permission_required(permission_codename, raise_exception=True):
	def decorator(view_func):
		@wraps(view_func)
		def _wrapped_view(request, *args, **kwargs):
			if User.objects.filter(is_admin=False, email=request.user):
				if admin_roles.objects.filter(user_id=request.user.id).exists():
					role = admin_roles.objects.filter(user_id=request.user.id)[0]
					if permission.objects.filter(codename=permission_codename).exists():
						perm = permission.objects.filter(codename=permission_codename)[0]
						if role_permissions.objects.filter(role_id=role.role_id, permission_id=perm.id,  delete=False).exists():
							# if request.user.user_permissions.filter(codename=permission_codename).exists():
							return view_func(request, *args, **kwargs)
				return page_error_403(request)
			else:
				return view_func(request, *args, **kwargs)
		return _wrapped_view
	return decorator


@login_required(login_url='mophy:login')
@permission_required('view_corridor', raise_exception=True)
def corridors_details(request):
	try:
		context = {}
		notifications_data = notifications(request)
		context.update(notifications_data)
		send_currency_list = settings.SEND_CURRENCY_LIST
		countries = settings.RECEIVE_CURRENCY_LIST
		array = []

		if request.method == 'POST':
			send_currency = request.POST.get('send_currency')
			if send_currency is not None:
				for s in send_currency_list:
					if s['currency'] == str(send_currency):
						s_index = send_currency_list.index(s)
						send_currency_list.pop(s_index)
						send_currency_list.insert(0, {'country': s['country'], 'currency': s['currency']})
		else:
			send_currency = "AUD"
		for c in countries:
			count = Transaction_details.objects.filter(send_currency=send_currency, receive_currency=c['currency']).count()
			send_amount = Transaction_details.objects.filter(send_currency=send_currency, receive_currency=c['currency']).aggregate(total=Sum('amount'))
			receive_amount = Transaction_details.objects.filter(send_currency=send_currency, receive_currency=c['currency']).aggregate(total=Sum('receive_amount'))
			if '.' in str(send_amount['total']):
				send_amount = round(float(send_amount['total']),2)
			else:
				send_amount = send_amount['total']
			if '.' in str(receive_amount['total']):
				receive_amount = round(float(receive_amount['total']),2)
			else:
				receive_amount = receive_amount['total']
			if send_amount is not None:
				comma =  comma_separated(exchange_rate=None, send_amount=send_amount, receive_amount=send_amount)
				send_amount = comma['send_amount']
			if receive_amount is not None:
				comma =  comma_separated(exchange_rate=None, send_amount=receive_amount, receive_amount=receive_amount)
				receive_amount = comma['receive_amount']
			dict = {'country': c['country'], 'currency': c['currency'], 'count': count, 'receive_amount': receive_amount, 'send_amount': send_amount}
			array.append(dict)
		context.update(data=array, send_currency_list=send_currency_list)
		return render(request, 'mophy/modules/corridors.html', context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
def risk_group_trasnactions_transaction_monitoring(send_currency, receive_currency):
	try:
		if send_currency is not None and receive_currency is not None:
			risk_group_transactions = {
			"very_high_pending_transactions": Transaction_details.objects.filter(send_currency=send_currency, receive_currency=receive_currency, risk_group="very high", payment_status=transaction['pending_payment']).count(),
			"very_high_approved_transactions": Transaction_details.objects.filter(send_currency=send_currency, receive_currency=receive_currency, risk_group="very high", tm_status=fn_approved).count(),
			"very_high_cancelled_transactions": Transaction_details.objects.filter(send_currency=send_currency, receive_currency=receive_currency, risk_group="very high", payment_status=transaction['cancelled']).count(),
			"very_high_queue_transactions": Transaction_details.objects.filter(send_currency=send_currency, receive_currency=receive_currency, risk_group="very high", tm_status=fn_queued).count(),

			"high_pending_transactions": Transaction_details.objects.filter(send_currency=send_currency, receive_currency=receive_currency, risk_group="high", payment_status=transaction['pending_payment']).count(),
			"high_approved_transactions": Transaction_details.objects.filter(send_currency=send_currency, receive_currency=receive_currency, risk_group="high", tm_status=fn_approved).count(),
			"high_cancelled_transactions": Transaction_details.objects.filter(send_currency=send_currency, receive_currency=receive_currency, risk_group="high", payment_status=transaction['cancelled']).count(),
			"high_queue_transactions": Transaction_details.objects.filter(send_currency=send_currency, receive_currency=receive_currency, risk_group="high", tm_status=fn_queued).count(),

			"very_low_pending_transactions": Transaction_details.objects.filter(send_currency=send_currency, receive_currency=receive_currency, risk_group="very low", payment_status=transaction['pending_payment']).count(),
			"very_low_approved_transactions": Transaction_details.objects.filter(send_currency=send_currency, receive_currency=receive_currency, risk_group="very low", tm_status=fn_approved).count(),
			"very_low_cancelled_transactions": Transaction_details.objects.filter(send_currency=send_currency, receive_currency=receive_currency, risk_group="very low", payment_status=transaction['cancelled']).count(),
			"very_low_queue_transactions": Transaction_details.objects.filter(send_currency=send_currency, receive_currency=receive_currency, risk_group="very low", tm_status=fn_queued).count(),

			"low_pending_transactions": Transaction_details.objects.filter(send_currency=send_currency, receive_currency=receive_currency, risk_group="low", payment_status=transaction['pending_payment']).count(),
			"low_approved_transactions": Transaction_details.objects.filter(send_currency=send_currency, receive_currency=receive_currency, risk_group="low", tm_status=fn_approved).count(),
			"low_cancelled_transactions": Transaction_details.objects.filter(send_currency=send_currency, receive_currency=receive_currency, risk_group="low", payment_status=transaction['cancelled']).count(),
			"low_queue_transactions": Transaction_details.objects.filter(send_currency=send_currency, receive_currency=receive_currency, risk_group="low", tm_status=fn_queued).count()
			}
		else:
			risk_group_transactions = {
			"very_high_pending_transactions": Transaction_details.objects.filter(risk_group="very high", payment_status=transaction['pending_payment']).count(),
			"very_high_approved_transactions": Transaction_details.objects.filter(risk_group="very high", tm_status=fn_approved).count(),
			"very_high_cancelled_transactions": Transaction_details.objects.filter(risk_group="very high", payment_status=transaction['cancelled']).count(),
			"very_high_queue_transactions": Transaction_details.objects.filter(risk_group="very high", tm_status=fn_queued).count(),

			"high_pending_transactions": Transaction_details.objects.filter(risk_group="high", payment_status=transaction['pending_payment']).count(),
			"high_approved_transactions": Transaction_details.objects.filter(risk_group="high", tm_status=fn_approved).count(),
			"high_cancelled_transactions": Transaction_details.objects.filter(risk_group="high", payment_status=transaction['cancelled']).count(),
			"high_queue_transactions": Transaction_details.objects.filter(risk_group="high", tm_status=fn_queued).count(),

			"very_low_pending_transactions": Transaction_details.objects.filter(risk_group="very low", payment_status=transaction['pending_payment']).count(),
			"very_low_approved_transactions": Transaction_details.objects.filter(risk_group="very low", tm_status=fn_approved).count(),
			"very_low_cancelled_transactions": Transaction_details.objects.filter(risk_group="very low", payment_status=transaction['cancelled']).count(),
			"very_low_queue_transactions": Transaction_details.objects.filter(risk_group="very low", tm_status=fn_queued).count(),

			"low_pending_transactions": Transaction_details.objects.filter(risk_group="low", payment_status=transaction['pending_payment']).count(),
			"low_approved_transactions": Transaction_details.objects.filter(risk_group="low", tm_status=fn_approved).count(),
			"low_cancelled_transactions": Transaction_details.objects.filter(risk_group="low", payment_status=transaction['cancelled']).count(),
			"low_queue_transactions": Transaction_details.objects.filter(risk_group="low", tm_status=fn_queued).count()
			}
		return risk_group_transactions
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False


@login_required(login_url='mophy:login')
@permission_required('view_stripe', raise_exception=True)
def stripe_page(request):
	try:
		context = {}
		notifications_data = notifications(request)
		context.update(notifications_data)
		id = stripecredentials.objects.first()
		if request.method == 'POST':
			form = stripeform(request.POST)
			if form.is_valid():
				for field in form:
					print("Field Error:", field.name,  field.errors)
				if id:
					obj = get_object_or_404(stripecredentials, id=str(id))
					form = stripeform(request.POST,instance=obj)
					if form.is_valid():
						form.save()
						context.update(form=form)
					return render(request, 'mophy/modules/stripe.html',context)
				else:
					user_obj = form.save()
					context.update(form=form)
				return render(request, 'mophy/modules/stripe.html', context)
		else:
			if id:
				obj = get_object_or_404(stripecredentials, id=str(id))
				form = stripeform(request.POST,instance=obj)
			else:
				form = stripeform(request.POST)
		context.update(form=form)
		return render(request, 'mophy/modules/stripe.html', context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
@login_required(login_url='mophy:login')
@permission_required('edit_currency_cloud', raise_exception=True)
def edit_currency_cloud(request):
	try:
		context = {}
		notifications_data = notifications(request)
		context.update(notifications_data)
		id = currencycloud.objects.first()
		if request.method == 'POST':
			form = currencycloudform(request.POST)
			if form.is_valid():
				if id:
					obj = get_object_or_404(currencycloud, id=str(id))
					form = currencycloudform(request.POST,instance=obj)
					if form.is_valid():
						form.save()
						context.update(form=form)
						return render(request, 'mophy/modules/currency_cloud.html', context)
				else:
					user_obj = form.save()
					context.update(form=form)
				return render(request, 'mophy/modules/currency_cloud.html', context)
		else:
			if id:
				obj = get_object_or_404(currencycloud, id=str(id))
				form = currencycloudform(instance=obj)
			else:
				form = currencycloudform()
		context.update(form=form)
		return render(request, 'mophy/modules/currency_cloud.html', context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

def update_transaction_activity_filter_lists(customer, send_currency, receive_currency, transaction_time):
	try:
		send_currency_list = settings.SEND_CURRENCY_LIST
		receive_currency_list = settings.RECEIVE_CURRENCY_LIST 
		time_list = [{"option":"7 Days", "value":"7"}, {"option":"30 Days", "value":"30"},{"option":"90 Days", "value":"90"},{"option":"1 Year", "value":"365"}]
		customers_list = list(User.objects.filter(is_superuser=False, is_admin=False, delete=False).values('email','id','customer_id').order_by('-id'))
		customers_list = [item for item in customers_list if item['customer_id'] is not None]

		if send_currency == None:
			send_currency_list = [dict(t) for t in set([tuple(d.items()) for d in send_currency_list])]
			send_currency_list.insert(0, {'country':'Choose currency', 'currency':None})
		if receive_currency == None:
			receive_currency_list = [dict(t) for t in set([tuple(d.items()) for d in receive_currency_list])]
			receive_currency_list.insert(0, {'country':'Choose currency', 'currency':None})
		if transaction_time == None:
			time_list = [dict(t) for t in set([tuple(d.items()) for d in time_list])]
			time_list.insert(0, {'option':'Choose interval', 'value':None})
		if customer == None:
			customers_list.insert(0, {'email':'Choose customer', 'customer_id': None, 'id': None})

		for s in customers_list:
			if s['customer_id'] == str(customer):
				customers_list.pop(customers_list.index(s))
				customers_list.insert(0, {'customer_id': s['customer_id'], 'email':s['email']})
				customers_list = [item for item in customers_list if item != {'email':'Choose customer', 'customer_id': None, 'id': None}]
				break 
		
		for s in send_currency_list:
			if s['currency'] == str(send_currency):
				send_currency_list.pop(send_currency_list.index(s))
				send_currency_list.insert(0, {'country': s['country'], 'currency':s['currency']})
				send_currency_list = [item for item in send_currency_list if item != {'country': 'Choose currency', 'currency': None}]
				break

		for r in receive_currency_list:
			if r['currency'] == str(receive_currency):
				receive_currency_list.pop(receive_currency_list.index(r))
				receive_currency_list.insert(0, {'country': r['country'], 'currency':r['currency']})
				receive_currency_list = [item for item in receive_currency_list if item != {'country': 'Choose currency', 'currency': None}]
				break

		if transaction_time != None:
			for t in time_list:
				if str(t['value']) == str(transaction_time):
					time_list.pop(time_list.index(t))
					time_list.insert(0, {'option': t['option'], 'value':t['value']})
					time_list = [item for item in time_list if item != {'option': 'Choose interval', 'value': None}]
					break
		return {'customers_list':customers_list, 'send_currency_list':send_currency_list, 'receive_currency_list': receive_currency_list,'time_list':time_list}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
def transaction_acitivity_filter_apply(customer, send_currency, receive_currency, transaction_time):
	try:
		if transaction_time is not None:
			today = date.today()  
			one_year_ago = today - timedelta(days=int(transaction_time))
			all_transactions = list(Transaction_details.objects.filter(date__gte=one_year_ago, date__lte=today))
		else:
			all_transactions = list(Transaction_details.objects.all())

		if customer != None and customer != "All":
			all_transactions = list(Transaction_details.objects.filter(customer_id=str(customer)))

		if send_currency != None:
			all_transactions = [i for i in all_transactions if str(i.send_currency).upper() == str(send_currency).upper()]

		if receive_currency != None:
			all_transactions = [i for i in all_transactions if str(i.receive_currency).upper() == str(receive_currency).upper()]

		pending_transactions = 0
		cancelled_pm_transactions = 0
		processed_transactions = 0
		incomplete_transactions = 0
		approved_transactions = 0
		pending_review_and_processing_transactions = 0
		cancelled_transactions = 0
		queued_transactions = 0
		very_high_risk_transactions = 0
		high_risk_transactions = 0 
		very_low_risk_transactions = 0
		low_risk_transactions = 0

		for i in all_transactions:
			if i.payment_status == transaction['pending_payment']:
				pending_transactions+= 1
			if i.payment_status == transaction['cancelled']:
				cancelled_pm_transactions+= 1
			if i.payment_status == transaction['completed']:
				processed_transactions+= 1
			if i.payment_status == transaction['incomplete']:
				incomplete_transactions+= 1
			if i.payment_status == transaction['pending_review']:
				pending_review_and_processing_transactions+= 1
			if i.tm_status == fn_approved:
				approved_transactions+= 1
			if i.tm_status == fn_cancelled:
				cancelled_transactions+= 1
			if i.tm_status == fn_queued:
				queued_transactions+= 1
			if i.risk_group == "very high":
				very_high_risk_transactions+= 1
			if i.risk_group == "high":
				high_risk_transactions+= 1
			if i.risk_group == "very low":
				very_low_risk_transactions+= 1		
			if i.risk_group == "low":
				low_risk_transactions+= 1
		return {'pending_transactions':pending_transactions,'cancelled_pm_transactions':cancelled_pm_transactions,'processed_transactions':processed_transactions,'incomplete_transactions':incomplete_transactions,'pending_review_and_processing_transactions':pending_review_and_processing_transactions,'approved_transactions':approved_transactions,'cancelled_transactions':cancelled_transactions,'queued_transactions':queued_transactions,'very_high_risk_transactions':very_high_risk_transactions,'high_risk_transactions':high_risk_transactions,'very_low_risk_transactions':very_low_risk_transactions,'low_risk_transactions':low_risk_transactions}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
@login_required(login_url='mophy:login')
@permission_required('view_activity_report', raise_exception=True)
def transaction_activity_report(request):
	try:
		context = {}
		context2 = {}
		notifications_data = notifications(request)
		context.update(notifications_data)
		customer = None
		send_currency = None
		receive_currency = None
		transaction_time = None

		if request.method == 'POST':
			customer = request.POST.get('customer')
			send_currency = request.POST.get('send_currency')
			receive_currency = request.POST.get('receive_currency')
			transaction_time = request.POST.get('transaction_time')

		updated_filter_lists = update_transaction_activity_filter_lists(customer, send_currency, receive_currency, transaction_time)
		context.update(updated_filter_lists)
		context2.update(updated_filter_lists)
		context.update(total_transactions =  Transaction_details.objects.all().count(), customers_list= updated_filter_lists['customers_list'], time_list = updated_filter_lists['time_list'],  send_currency_list = updated_filter_lists['send_currency_list'], receive_currency_list= updated_filter_lists['receive_currency_list'])
		context2.update(total_transactions =  Transaction_details.objects.all().count(), customers_list= updated_filter_lists['customers_list'], time_list = updated_filter_lists['time_list'],  send_currency_list = updated_filter_lists['send_currency_list'], receive_currency_list= updated_filter_lists['receive_currency_list'])
		filtered_data = transaction_acitivity_filter_apply(customer, send_currency, receive_currency, transaction_time)
		context2.update(filtered_data)

		context.update(filtered_data)
		all_zero = all(value == 0 for value in filtered_data.values())
		if all_zero:
			context.update(all_zero = "No Transactions Found")
			context2.update(all_zero = "No Transactions Found")
		context_json = json.dumps(context2)
		context.update(context_json = context_json, data = context)
		return render(request, 'mophy/transaction_activity.html', context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

@login_required(login_url='mophy:login')
@permission_required('view_transaction', raise_exception=True)
def receipt(request, id):
	try:
		response = generate_pdf_receipt(id)
		return response
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
        
@login_required(login_url='mophy:login')
@permission_required('view_currency_cloud', raise_exception=True)
def currency_cloud(request):
	try:
		context = {}
		notifications_data = notifications(request)
		context.update(notifications_data)
		data = currencycloud.objects.all()
		context.update(data=data)
		return render(request, "mophy/modules/currency_cloud.html",context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False


@login_required(login_url='mophy:login')
def download_csv(request):
	data_list = []
	context = {}
	try:
		if request.method == 'POST':
			key = request.POST.get('csv_key')
			value = request.POST.get('csv_value')
			type = request.POST.get('type')

			request.session['type'] = type
			request.session['csv_key'] = key
			request.session['csv_value'] = value
			return JsonResponse({'success':True})
		
		key = request.session.get('csv_key', None)
		val = request.session.get('csv_value', None)
		type = request.session.get('type', None)
		if str(key).lower() != "null" and str(val).lower() != "null":
			value = next((item[val] for item in CSV_DB_VALUES_ if val in item), val)
		else:
			key = None
			value = None
		if str(type).lower() == "customer":
			user_data = get_csv_user_data(key, value)
			data = user_data['data_list']
		else:
			trans_data = get_csv_transaction_data(key, value)
			data = trans_data['data_list']
		return Download_csv(data ,type)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False


@login_required(login_url='mophy:login')
@permission_required('edit_customer', raise_exception=True)
def edit_user(request,id):
	try:
		context = {}
		notifications_data = notifications(request)
		context.update(notifications_data)
		obj = get_object_or_404(User,customer_id=id)	
		country = CountryInfo(obj.location)
		code = country.calling_codes()
		country_list = list(user_countries.values())
		if obj.country_code in country_list:
			country_list.remove(obj.country_code)
			country_list.insert(0, obj.country_code)
		context.update(country_list =country_list)
		context_json = json.dumps(context)
		context.update(context_json=context_json, country_code="+"+str(code[0]))
		user_obj = get_object_or_404(User,customer_id=id)
		if request.method == 'POST':
			form = EditUserForm(request.POST, instance=user_obj)
			for field in form:
				print("Field Error:", field.name,  field.errors)
			if form.is_valid():
				user_obj = form.save()
				country = CountryInfo(user_obj.location)
				code = country.calling_codes()
				iso = country.alt_spellings()
				User.objects.filter(country_code=iso[0], customer_id=user_obj.customer_id).update(mobile="+"+str(code[0])+str(user_obj.mobile))
				return redirect('mophy:users')
		else:
			form = EditUserForm(instance=user_obj)
			context.update(form=form)
		return render(request, 'mophy/modules/edit_user.html', context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
@login_required(login_url='mophy:login')
def send_otp(request):
	try:
		if request.method == 'POST':
			otp_value = None
			otp_value = request.POST.get('otp')
			if otp_value == None:
				otp = str(generate_activation_code())
				if User.objects.filter(otp=otp).exists():
					otp = str(generate_activation_code())
				if not User.objects.filter(is_superuser=True, is_admin=True, delete=False).exists():
					return JsonResponse({'success':False,'message':"User not found"})
				mobile = User.objects.filter(is_superuser=True,  is_admin=True, delete=False).values('mobile')
				mobile = mobile[0]['mobile']
				User.objects.filter(is_superuser=True, mobile=mobile,  is_admin=True, delete=False).update(otp=otp)
				send_sms(mobile, otp)
				return JsonResponse({'success':True,'message':"OTP has been sent to your registered mobile number"})
			else:
				if not User.objects.filter(is_superuser=True, is_admin=True, otp=otp_value, delete=False).exists():
					return JsonResponse({'success':False,'message':"Invalid OTP"})
				else:
					return JsonResponse({'success':True,'message':"OTP has been verified successfully. Now you can change your password."})
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
		
@login_required(login_url='mophy:login')
def change_password(request):
	try:
		context = {}
		notifications_data = notifications(request) 
		context.update(notifications_data)
		if request.method == 'POST':	
			form = PasswordChangeForm(request.user,request.POST)
			for field in form:
				print("Field Error:", field.name,  field.errors)
			if form.is_valid():			
				user = form.save()
				update_session_auth_hash(request, user)
				messages.success(request, 'Password updated successfully')
				User.objects.filter(is_superuser=True, is_admin=True, delete=False).update(otp=None)
				return redirect('mophy:change-password')
			else:
				pass
				# messages.warning(request, 'Form is not valid. Please correct the errors.')
		else:
			form = PasswordChangeForm(request.user)
		context.update(form=form)
		return render(request, 'mophy/modules/change-password.html', context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

@login_required(login_url='mophy:login')
@permission_required('delete_recipient', raise_exception=True)
def delete_recipient(request,id):
	try:
		bank_id = id
		recipient_id = Recipient_bank_details.objects.filter(id=id).values('recipient_id')
		recipient_id = recipient_id[0]['recipient_id']
		user_id = Recipient.objects.filter(id=recipient_id).values('user_id')
		user_id = user_id[0]['user_id']
		customer_id = User.objects.filter(id=user_id).values('customer_id')
		b = Recipient_bank_details.objects.get(id=id)
		b.delete()
		r = Recipient.objects.get(id=recipient_id)
		r.delete()
		messages.success(request, "Recipient deleted successfully") 
		return redirect('mophy:user-details', id=customer_id[0]['customer_id'])
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
@login_required(login_url='mophy:login')
@permission_required('create_customer', raise_exception=True)
def create_customer(request):
	try:
		context = {}
		notifications_data = notifications(request)
		context.update(notifications_data)
		if request.method == 'POST':
			print("i")
		return render(request, 'mophy/modules/create_customer.html', context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False


@login_required(login_url='mophy:login')
@permission_required('create_customer', raise_exception=True)
def add_user(request):
	try:
		context = {}
		notifications_data = notifications(request)
		context.update(notifications_data)
		if request.method == 'POST':
			form = NewUserForm(request.POST, request.FILES)
			for field in form:
				print("Field Error:", field.name,  field.errors)
			if form.is_valid():
				user_obj = form.save()
				country = CountryInfo(user_obj.location)
				code = country.calling_codes()
				iso = country.alt_spellings()
				cust_id =  create_customer_id(country_code=str(iso[0]).upper(), id=user_obj.id)
				User.objects.filter(id=user_obj.id).update(mobile="+"+str(code[0])+user_obj.mobile,customer_id=cust_id, country_code=str(iso[0]).upper())
				# user_obj.groups.clear()
				# for i in form.cleaned_data.get('groups'):
				# 	user_obj.groups.add(i)
				messages.success(request,f'{user_obj.First_name} {user_obj.Last_name} is created successfully')
				return redirect('mophy:users')
		else:
			form = NewUserForm()
		return render(request, 'mophy/modules/add_user.html', {'form':form, 'context':context})
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
@login_required(login_url='mophy:login')
@permission_required('create_recipient', raise_exception=True)
def add_recipient(request, id):
	try:
		context = {}
		notifications_data = notifications(request)
		customer_id = User.objects.filter(id=id).values('customer_id')
		country_list = list(recipient_countries.values())	
		context.update(notifications_data)
		context.update(user_id=id, customer_id=customer_id[0]['customer_id'])
		if request.method == 'POST':
			bank_name = request.POST.get('bank_name')
			account_name = request.POST.get('account_name')
			account_number = request.POST.get('account_number')
			user_id = Recipient(user_id=id)
			recipient_id = Recipient_bank_details(recipient_id=0)
			bank_form = NewRecipientBankForm(request.POST, instance=recipient_id)
			for field in bank_form:
				print("Field Error:", field.name,  field.errors)
			if bank_form.is_valid():
				bank_obj = bank_form.save()
			user_id = Recipient(user_id=id)
			form = NewRecipientForm(request.POST, instance=user_id)
			for field in form:
				print("Field Error:", field.name,  field.errors)
			if form.is_valid():
				obj = form.save()
				country = CountryInfo(obj.country)
				code = country.calling_codes()
				iso = country.alt_spellings()
				Recipient.objects.filter(id=obj.id).update(user_id=id, mobile="+"+str(code[0])+str(obj.mobile), country_code = iso[0])
				Recipient_bank_details.objects.create(recipient_id=obj.id, bank_name=bank_name, account_name=account_name, account_number=account_number)
				messages.success(request,f'{obj.first_name} {obj.last_name} is created successfully')
				return redirect('mophy:user-details', id=customer_id[0]['customer_id'])
		else:
			form = NewRecipientForm()
			bank_name = NewRecipientBankForm()
		return render(request, 'mophy/modules/add_recipient.html', {'bank_name':bank_name,'form':form, 'notifications_data':notifications_data, 'context':context})
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
@login_required(login_url='mophy:login')
@permission_required('delete_transaction', raise_exception=True)
def delete_transaction(request,id):
	id = int(id)
	u = Transaction_details.objects.get(id=id)
	u.delete()
	messages.success(request, "Transaction deleted successfully") 
	return redirect('mophy:transactions')

@csrf_exempt
def login_user(request):
	try:
		context = {}
		current_year = datetime.now().year
		message=''
		error = None
		if request.method == 'POST':
			csrf_token = request.POST.get('csrfmiddlewaretoken', '')
			form = LoginForm(request.POST)
			if form.is_valid():
				user=form.login(request)
				if user is not None and user.delete == False:
					login(request, user)
					usergroup = ','.join(request.user.groups.values_list('name',flat = True))
					messages.success(request,f'Welcome To Dashboard')
					next_url = request.GET.get('next')
					if next_url:
						return HttpResponseRedirect(next_url)
					else:
						return redirect('mophy:index')
				else:
					error="Your account access has been restricted. For assistance, please contact the administrator."
			else:
				error='Invalid credentials'
				return render(request, 'mophy/modules/login.html', context={'form': form, 'error':error, 'current_year':current_year})
		else:
			if request.user.is_authenticated:
				return redirect('mophy:index')
			form = LoginForm()
		return render(request, 'mophy/modules/login.html', context={'form': form, 'error':error,  'current_year':current_year})
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
def logout_user(request):
	logout(request)
	messages.success(request,'Logout Successfully')	
	return redirect('mophy:login')





@login_required(login_url='mophy:login')
def search_zai_user(request):
	try:
		if request.method == "POST":
			zai_user_id = request.POST.get('zai_user_id')
			zai_email = request.POST.get('zai_email')
			if str(zai_user_id).strip() != '' and str(zai_email).strip() != '':
				if not zai_payid_details.objects.filter(zai_email=zai_email).exists():
					if not zai_agreement_details.objects.filter(zai_email=zai_email).exists():
						return JsonResponse({'success':False, 'message':"User not found"})		
					else:
						zai_data = zai_agreement_details.objects.filter(zai_email=zai_email).values('zai_user_id')[0]
				else:
					zai_data = zai_payid_details.objects.filter(zai_email=zai_email).values('zai_user_id')[0]
				if str(zai_user_id).lower() != str(zai_data['zai_user_id']).lower():
					return JsonResponse({'success':False, 'message':"User ID and email does not match."})		
			elif str(zai_user_id).strip() == '':
				if zai_payid_details.objects.filter(zai_email=zai_email).exists():
					zai_data = zai_payid_details.objects.filter(zai_email=zai_email).values('zai_user_id')[0]
				elif zai_agreement_details.objects.filter(zai_email=zai_email).exists():
					zai_data = zai_payid_details.objects.filter(zai_email=zai_email).values('zai_user_id')[0]
				else:
					return JsonResponse({'success':False, 'message':"User not found"})		
				zai_user_id = zai_data['zai_user_id']
			else:
				if zai_payid_details.objects.filter(zai_user_id=zai_user_id).exists():
					zai_data = zai_payid_details.objects.filter(zai_user_id=zai_user_id).values('zai_email')[0]
				elif zai_agreement_details.objects.filter(zai_user_id=zai_user_id).exists():
					zai_data = zai_payid_details.objects.filter(zai_user_id=zai_user_id).values('zai_email')[0]
				else:
					return JsonResponse({'success':False, 'message':"User not found"})		
				zai_email = zai_data['zai_email']
			# user_response = get_user_with_id(request, zai_user_id)
			# if 'users' in user_response:
			# 	if str(zai_email).lower() == str(user_response['users']['email']):
			balance_response = get_wallet_balance(zai_user_id, request)
			return JsonResponse({'success':True, 'wallet_balance':balance_response['wallet_balance'], 'zai_email':zai_email, 'zai_user_id':zai_user_id})
			# response = zai_search_email_id(zai_token(request), zai_email)
			# if 'users' in response:
			# 	for u in response['users']:
			# 		if u['email'] == str(zai_email).lower():
			# 			zai_user_id = u['id']
			# 			balance_response = get_wallet_balance(zai_user_id, request)
			# 			return JsonResponse({'success':True, 'wallet_balance':balance_response['wallet_balance'], 'zai_email':zai_email})
			# return JsonResponse({'success':False, 'message':"User not found"})
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

@login_required(login_url='mophy:login')
def get_zai_balance(request):
	if request.method == 'POST':
		ra_user_id = request.POST.get('ra_user_id')
		balance_response = get_wallet_balance(zai_user_id=ra_user_id, request=request)
	return JsonResponse({'success':True, 'wallet_balance':balance_response['wallet_balance'],'zai_email':balance_response['zai_email']})

def send_reset_password_otp(request):
	try:
		otp = None
		mobile = None
		password = None
		if request.method == 'POST':
			mobile = request.POST.get('mobile')
			otp = request.POST.get('otp')
			password = request.POST.get('password')
			country_code = request.POST.get('country_code')
			if str(mobile[0]) == "0":
				mobile = str(mobile[1:])
			new_mobile = str(country_code)+str(mobile)
			if not User.objects.filter(mobile=new_mobile,is_admin=True, is_superuser=True, delete=False).exists():
				return JsonResponse({'success':False,'message':"Mobile does not exists!"})
			id = User.objects.filter(mobile=new_mobile, is_superuser=True, is_admin=True, delete=False).values('id')
			user = User.objects.get(id= id[0]['id'])
			if str(otp) == '' or otp == None:
				otp = str(generate_activation_code())
				if User.objects.filter(otp=otp).exists():
					otp = str(generate_activation_code())
				User.objects.filter(id=id[0]['id']).update(otp=otp, updated_at=timezone.now())
				send_sms(mobile, otp)
				return JsonResponse({'type':"otp",'success':True,'message':"OTP has been sent on your registered mobile number"})
			if str(password) == '' or password == None:
				if str(otp) != '' or otp != None:
					if not User.objects.filter(id=id[0]['id'], otp=otp).exists():
						return JsonResponse({'type':"otp",'success':False,'message':"Invalid OTP"})
					is_verified = User.objects.filter(id=id[0]['id']).values('updated_at')          
					token_created_at = is_verified[0]['updated_at']
					expire_time = token_created_at + settings.RESET_PASSWORD_TOKEN_EXPIRED
					is_token_expired =  expire_time < timezone.now()
					if is_token_expired == True:
						return JsonResponse({'type':"otp",'success':False,'message':"OTP Expired"})
					return JsonResponse({'type':"password",'success':True,'message':"Please change your password"})
			if str(password) != '' or password != None:
				user.set_password(password)
				user.save()
				return JsonResponse({'type':'updated','success':True,'message':"Password Updated Successfully!"})
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
				


# @login_required(login_url='mophy:login')
# @permission_required('view_loyality_program', raise_exception=True)
# def referral_detail(request, id): #id is user_id
# 	context = {}	
# 	notifications_data = notifications(request)
# 	context.update(notifications_data)
# 	referral_data = list(referral.objects.all().values('id','name','referral_type_id__type'))
# 	array = []
# 	print(referral_data)
# 	#updating details of customer who referred this customer
# 	if referral_meta.objects.filter(referred_to=id).exists():
# 		ref_by = list(referral_meta.objects.filter(referred_to=id).values('user_id'))
# 		context.update(referred_by = get_object_or_404(User, id= ref_by[0]['user_id']))
# 	for i in referral_data:
# 		if referral_meta.objects.filter(user_id=id, referral_id=i['id']).exists():
# 			print(i['referral_type_id__type'])
# 			data = list(referral_meta.objects.filter(user_id=id, referral_id=i['id']).values('id','transaction_id','referral_id','claimed_date','referral_id__status','referred_by','referred_to','claimed','is_used','discount','referral_id__currency'))
# 			#checking is user invite any customer and if invites then referred to should not be none
# 			if str(i['referral_type_id__type']).lower() == str(referral_dict['invite']).lower():
# 				dt = list(referral_meta.objects.filter(referred_to__isnull=False,user_id=id, referral_id=i['id']).values('id','transaction_id','referral_id','claimed_date','referral_id__status','referred_by','referred_to','claimed','is_used','discount', 'referral_id__currency'))
# 				if len(dt) != 0:
# 					#getting invited customer details
# 					for d in dt:
# 						d.update(referred_to_user = get_object_or_404(User, id=d['referred_to']))
# 					array.append({'type':i['referral_type_id__type'], 'name':i['name'], 'data':dt, 'count':len(dt)})
# 			else:
# 				array.append({'type':i['referral_type_id__type'], 'name':i['name'], 'data':data, 'count':len(data)})
# 	context.update(array=array, user = get_object_or_404(User, id=id))
# 	print(array)
# 	return render(request,'mophy/referral_detail.html', context)

# @login_required(login_url='mophy:login')
# @permission_required('view_loyality_program', raise_exception=True)
# def referral_detail(request, id): #id is user_id
# 	context = {}	
# 	notifications_data = notifications(request)
# 	context.update(notifications_data)
# 	dict = {}
# 	referral_types = list(referral_type.objects.all().values('id','type'))
# 	type_ids = [id['id'] for id in referral_types]
# 	referral_data = list(referral.objects.filter(referral_type_id__in=type_ids))
# 	array = []
# 	for r in referral_data:
# 		if referral_meta.objects.filter(user_id=id).exists():
# 			data = list(referral_meta.objects.filter(user_id=id, referral_id=r.id).values('user_id__Last_name','user_id__First_name','user_id__email','user_id__customer_id','referred_by','referred_to','transaction_id','is_used','referral_id__name','referral_id__description','claimed_date','claimed'))
# 			for x in data:
# 				customer_name = str(x['user_id__First_name'])+" "+str(x['user_id__Last_name'])
# 				if str(customer_name) == "" or str(customer_name) == " ":
# 					customer_name = None
# 				context.update(customer_id=x['user_id__customer_id'], customer_email=x['user_id__email'], customer_name = customer_name)
# 				x.update(referred_by_amount = r.referred_by_amount, referred_to_amount = r.referred_to_amount)
# 				if x['referred_by'] != None and str(x['referred_by']) != "":
# 					x.update(referred_by_user = User.objects.filter(id=x['referred_by'])[0])
# 				if x['referred_to'] != None and str(x['referred_to']) != "":
# 					x.update(referred_to_user = User.objects.filter(id=x['referred_to'])[0])
# 				for key, value in x.items():
# 					if value is None or str(value).replace(" ","") == "":
# 						x[key] = 'None'
# 				dict.update(type= str(r.name).capitalize(), status=str(r.status).capitalize(),data=data, count=len(data))
# 				array.append(dict)
# 	context.update(array=array)
# 	return render(request,'mophy/referral_detail.html', context)

@login_required(login_url='mophy:login')
@permission_required('view_loyality_program', raise_exception=True)
def loyality_program(request):
	context = {}	
	notifications_data = notifications(request)
	context.update(notifications_data)
	meta = referral_meta.objects.all()
	data = referral.objects.all().values('id','currency','referral_type_id__type','referred_by_amount','referred_to_amount','name','description','status','start_date','end_date').order_by("-id")
	for item in data:
		for key, value in item.items():
			if value == '':
				item[key] = None
		if str(item['currency']) == '' or item['currency'] == None:
			item['currency'] == "AUD"
	context.update(data=data)
	return render(request,'mophy/loyality_program.html', context)

@login_required(login_url='mophy:login')
@permission_required('delete_loyality_program', raise_exception=True)
def delete_loyality_program(request, id):
	context = {}	
	notifications_data = notifications(request)
	context.update(notifications_data)
	# data = get_object_or_404(referral, id=id)
	# data.delete()
	return redirect('mophy:loyality-program')

@login_required(login_url='mophy:login')
@permission_required('create_loyality_program', raise_exception=True)
def add_loyality_program(request):
	context = {}	
	notifications_data = notifications(request)
	context.update(notifications_data)
	type_data = settings.REFERRAL_TYPES
	for i in type_data:
		if not is_obj_exists(referral_type, {'type':i}):
			create_model_obj(referral_type, {'type':i})
	data = referral_type.objects.all()
	context.update(data=data)
	if request.method == "POST":
		start_date = None
		end_date = None
		referral_type_name = request.POST.get('referral_type')
		name = request.POST.get('name')
		description = request.POST.get('description')
		status = request.POST.get('status')
		currency = request.POST.get('currency')
		discount = request.POST.get('discount')
		referred_by = request.POST.get('referred_by')
		referred_to = request.POST.get('referred_to')
		start_date = request.POST.get('start_date')
		end_date = request.POST.get('end_date')

		referral_type_data = get_object_or_404(referral_type, type=str(referral_type_name).lower())
		
		if referral.objects.filter(referral_type_id=referral_type_data.id, currency = str(currency).upper()).exists():
			return JsonResponse({'success':False, 'message':"Loyality Program already exists!"})
		#invite obj 
		if discount == None or str(discount) == '':
			referral.objects.create(referred_by_amount=referred_by, referred_to_amount=referred_to, currency=str(currency).upper(), name=name, description=description, status=status, referral_type_id=referral_type_data.id, start_date=start_date, end_date=end_date)
		else:
			referral.objects.create(referred_by_amount=discount, referred_to_amount=discount, currency=str(currency).upper(), name=name, description=description, status=status, referral_type_id=referral_type_data.id, start_date=start_date, end_date=end_date)
		return JsonResponse({'success':True, 'message':"New Loyality Program created succesfully"})
	else:
		return render(request,'mophy/add_voucher.html', context)

@login_required(login_url='mophy:login')
@permission_required('create_loyality_program', raise_exception=True)
def edit_loyality_program(request, id):  #id is referral id
	context = {}	
	notifications_data = notifications(request)
	context.update(notifications_data)
	if referral.objects.filter(id=id).exists():
		data = referral.objects.filter(id=id).values('id','currency','referral_type_id__type','referred_by_amount','referred_to_amount','name','description','status','start_date','end_date')
		context.update(data=data[0])
	if request.method == "POST":
		name = request.POST.get('name')
		description = request.POST.get('description')
		status = request.POST.get('status')
		start_date = request.POST.get('start_date')
		end_date = request.POST.get('end_date')
		discount = request.POST.get('discount')
		referred_by = request.POST.get('referred_by')
		referred_to = request.POST.get('referred_to')
		if str(status) == '' or status == None:
			status = data[0]['status']
		if str(data[0]['referral_type_id__type']).lower() == "invite":
			referral.objects.filter(id=id).update(name=name, referred_by_amount=referred_by, referred_to_amount=referred_to, description=description, status= str(status).lower(), start_date=start_date, end_date=end_date)
		else:
			referral.objects.filter(id=id).update(name=name, referred_by_amount=discount, referred_to_amount=discount, description=description, status= str(status).lower(), start_date=start_date, end_date=end_date)
		return redirect('mophy:loyality-program')
	else:
		return render(request,'mophy/edit_loyality_program.html', context)
	
def get_referral_amount(request):
	if request.method == "POST":
		referred_to = 0
		referred_by = 0		
		referral_type_id = request.POST.get('referral_type')
		if referral.objects.filter(referral_type_id=referral_type_id).exists():
			data = referral.objects.filter(referral_type_id=referral_type_id).values('referred_by_amount','referred_to_amount')
			# if data[0]['referred_to_amount'] is not None:
			# 	referred_to = data[0]['referred_to']
			# if data[0]['referred_by'] is not None:
			# 	referred_by = data[0]['referred_by']
		return JsonResponse({'success':True, 'referred_to':referred_to, 'referred_by':referred_by})
	

#transfer funds from uuser wallet to WidophRemit wallet
@login_required(login_url='mophy:login')
def zai_user_transfer(request):
	try:
		context = {}
		notifications_data = notifications(request)
		context.update(notifications_data)
		if request.method == 'POST':
			zai_email = request.POST.get('zai_email')
			amount = request.POST.get('amount')
			type = request.POST.get('type')
			ra_user_id = request.POST.get('ra_user_id')
			response = zai_search_email_id(zai_token(request), zai_email)
			if 'users' in response:
				for u in response['users']:
					if u['email'] == str(zai_email).lower():
						zai_user_id = u['id']		
			time = timezone.now().time()
			reference_no = "RA"+str(time.second)+str(time.microsecond)
			#get wallet balance
			wallet_respone = zai_get_user_wallet(access_token=zai_token(request), zai_user_id=zai_user_id)
			if not 'wallet_accounts' in wallet_respone:
				return JsonResponse({'success':False})
			wallet_id = wallet_respone['wallet_accounts']['id'] 
			wallet_blnc = str(wallet_respone['wallet_accounts']['balance'])
			if len(wallet_blnc) == 2:
				wallet_blnc = int(wallet_blnc) / 100.0
			else:
				wallet_blnc = int(wallet_blnc) / 100
			if float(amount) > float(wallet_blnc): 
				return JsonResponse({'success':False, 'message':"Insufficient balance in user wallet."})
			#create item
			item_response = zai_create_item(seller_id=ra_user_id, access_token=zai_token(request), payment_id=reference_no, amount_reason="Wallet Transfer", send_amount=str(amount), zai_user_id=zai_user_id, send_currency="AUD")
			if 'errors' in item_response:
				return JsonResponse({'success':False, 'message':item_response['errors']})
			payment_response = zai_make_payment(item_id=item_response['items']['id'], wallet_account_id=wallet_id, access_token=zai_token(request))
			if 'errors' in payment_response:
				return JsonResponse({'success':False, 'message':payment_response['errors']})
			ra_wallet_respone = zai_get_user_wallet(access_token=zai_token(request), zai_user_id=ra_user_id)
			comma =  comma_separated(exchange_rate=None, send_amount = wallet_respone['wallet_accounts']['balance'], receive_amount = ra_wallet_respone['wallet_accounts']['balance'])
			if zai_admin_users.objects.filter(zai_user_id=ra_user_id).exists():				
				destination_bank = zai_admin_users.objects.filter(zai_user_id=ra_user_id).values('bank_name')
				destination_bankname = destination_bank[0]['bank_name']
			else:
				for user in ZAI_ADMIN_USERS:
					if user['zai_user_id'] == ra_user_id:
						destination_bankname = user['bank_name']
			ra_wallet = get_wallet_balance(zai_user_id=ra_user_id, request=request)
			withdraw_zai_funds.objects.create(type="User Wallet Transfer", source_id=zai_user_id, destination_id=destination_bankname, wallet_id=wallet_id, status="completed", amount=amount, wallet_balance = ra_wallet['wallet_balance'], reference_id=reference_no)
			return JsonResponse({'success':True, 'ra_balance':"{0:,.2f}".format(int(ra_wallet_respone['wallet_accounts']['balance']) / 100), 'balance':"{0:,.2f}".format(int(wallet_respone['wallet_accounts']['balance']) / 100), 'message':"Funds has been tranferred to WidophRemit wallet."})
		else:
			return render(request,'mophy/user_transfer.html', context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(str(e)+" in line "+str(exc_tb.tb_lineno))
		return JsonResponse({'success':False, 'message':str(e)+" in line "+str(exc_tb.tb_lineno)})



@login_required(login_url='mophy:login')
# @permission_required('view_loyality_program', raise_exception=True)
def assign_permissions_to_user(request,id):
	try:
		context = {}
		user_permissions_list = []
		all_permissions = []
		notifications_data = notifications(request)
		context.update(notifications_data)
		permissions_list = list(permission.objects.all().values('name'))
		for x in permissions_list:
			all_permissions.append(x['name'])
		user = get_object_or_404(User, id=id)
		user_permissions = user.user_permissions.all().values('name')
		for x in user_permissions:
			user_permissions_list.append(x['name'])
		context.update(permissions=all_permissions, id=id, user_permissions=user_permissions_list)
		if request.method == 'POST':
			value = request.POST.get('permission')
			remove_value = request.POST.get('remove_permission')
			user = get_object_or_404(User, id=id)
			if remove_value is not None:
				permission_id = permission.objects.get(name=remove_value)
				if user.user_permissions.filter(id=permission_id.id).exists():
					user.user_permissions.remove(permission_id.id)
					user_permissions_list.remove(remove_value)
				return JsonResponse({'success':True, 'user_permissions':list(user_permissions_list)})
			if value != None:
				if permission.objects.filter(name=value).exists():
					permission_id = permission.objects.get(name=value)
					if not user.user_permissions.filter(id=permission_id.id).exists():
						user.user_permissions.add(permission_id)	
						user_permissions_list.append(value)
						return JsonResponse({'success':True, 'user_permissions':list(user_permissions_list)})
					else:
						return JsonResponse({'success':False, 'message':"Permission already added"})
				return JsonResponse({'success':True, 'user_permissions':list(user_permissions_list)})
			else:
				return JsonResponse({'success':False, 'message':"Invalid Permission"})
		else:
			return render(request, 'mophy/modules/assign_permissions_to_user.html',context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

@login_required(login_url='mophy:login')
@permission_required('create_admin_user', raise_exception=True)
def add_admin_user(request):
	context = {}
	notifications_data = notifications(request)
	context.update(notifications_data)
	context.update(roles_list = list(roles.objects.all()))
	if request.method == 'POST':
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		email = request.POST.get('email')
		role_id = request.POST.get('role')
		password = request.POST.get('password')
		# checking email
		if User.objects.filter(email=email).exists():
			return JsonResponse({'success':False, 'message': "Email already exists!" })
		# creating user in Database
		if User.objects.filter(is_superuser=True, email=email, delete=True).exists():
			User.objects.filter(is_superuser=True, email=email).update(First_name=first_name, Last_name=last_name, delete=False)
			user = get_object_or_404(User, email=email)
		else:
			user = User.objects.create(First_name=first_name, Last_name=last_name, email=email, is_superuser=True, is_staff=True, is_admin=False)
		user.set_password(password)
		user.save()
		if not admin_roles.objects.filter(user_id=user.id).exists():
			admin_roles.objects.create(user_id=user.id, role_id=role_id)
		else:
			admin_roles.objects.filter(user_id=user.id).update(role_id=role_id)
		messages.success(request,f'{first_name} {last_name} is created successfully')
		return JsonResponse({'success':True, 'redirect_url':settings.BASE_URL+"/adminpanel/admin-users" , 'message': "User created successfully" })
	else:
		return render(request, 'mophy/modules/add_admin_user.html',context)

@login_required(login_url='mophy:login')
@permission_required('edit_admin_user', raise_exception=True)
def edit_admin_user(request, id):
	context = {}
	notifications_data = notifications(request)
	context.update(notifications_data)
	user_role = None
	user_role_id = None
	user_obj = get_object_or_404(User,id=id)
	if user_obj:
		if admin_roles.objects.filter(user_id=user_obj.id).exists():
			role_data = admin_roles.objects.filter(user_id=user_obj.id).values('role_id__name', 'role_id')[0]
			user_role = role_data['role_id__name']
			user_role_id = role_data['role_id']
		context.update(user_obj=user_obj, user_role = user_role, roles_data=roles.objects.all())
	if request.method == 'POST':
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		email = request.POST.get('email')
		role_id = request.POST.get('role')
		if str(first_name).replace(" ","") == "" and str(last_name).replace(" ","") == "":
			context.update(error="Please enter First Name and Last Name")
			return render(request, 'mophy/modules/edit_admin_user.html',context)		
		if email is not None:
			if str(email).lower() != str(user_obj.email).lower() and User.objects.filter(email=email, is_superuser=True, delete=False).exists():
				context.update(error="Email already exists!")
				return render(request, 'mophy/modules/edit_admin_user.html',context)
		if user_role == None and role_id == None:
			context.update(error="Please select role")
			return render(request, 'mophy/modules/edit_admin_user.html',context)
		if role_id != None and user_role != None:
			if str(role_id) == str(user_role_id):
				context.update(error="Role already exists!")
				return render(request, 'mophy/modules/edit_admin_user.html',context)			
		elif role_id == None and user_role_id != None:
			role_id = user_role_id
		if role_id != None and admin_roles.objects.filter(user_id=user_obj.id).exists():
			admin_roles.objects.filter(user_id=user_obj.id).update(role_id=role_id)
		else:
			admin_roles.objects.create(user_id=user_obj.id, role_id=role_id)
		User.objects.filter(id=user_obj.id).update(email=email, First_name=first_name, Last_name = last_name)
		messages.success(request,'User Updated Sucessfully')
		return redirect('mophy:admin-users')
	else:
		return render(request, 'mophy/modules/edit_admin_user.html',context)
	
@login_required(login_url='mophy:login')
@permission_required('view_group', raise_exception=True)
def groups_list(request):
	context={
		# "groups":Group.objects.annotate(user_count=Count('newuser',distinct=True)).annotate(perms_count=Count('permissions',distinct=True)),
		"groups":Group.objects.all(),
		"colors":{'primary':'primary','success':'success','dark':'dark'}
	}
	return render(request, 'mophy/modules/group-list.html', context)

@login_required(login_url='mophy:login')
@permission_required('edit_group', raise_exception=True)
def group_edit(request,id):
	group_obj = get_object_or_404(Group,id=id)

	if request.method == 'POST':
		queryDict = request.POST
		data = dict(queryDict)

		try:
			group_obj.name = data['name'][0]
			group_obj.save()
		except:
			response = JsonResponse({"error": "Group Name already exist"})
			response.status_code = 403
			return response

		if 'permissions[]' in data:
			group_obj.permissions.clear()
			group_obj.permissions.set(data['permissions[]'])
		else:
			group_obj.permissions.clear()

	
		response = JsonResponse({"success": "Save Successfully"})
		response.status_code = 200
		return response

	else:
		form = GroupForm(instance=group_obj)
	return render(request, 'mophy/modules/group-edit.html',{'form': form})

@login_required(login_url='mophy:login')
@permission_required('delete_group', raise_exception=True)
def group_delete(request,id):
	g=get_object_or_404(Group,id=id)
	g.delete()
	messages.success(request,'Group Deleted Sucessfully')
	return redirect('mophy:groups')

@login_required(login_url='mophy:login')
@permission_required('create_group', raise_exception=True)
def group_add(request):
	if request.method == 'POST':
		form = GroupForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request,'Group Created Successfully')
			return redirect('mophy:groups')
		else:
			messages.warning(request,'Name Already Exist')
			return render(request, 'mophy/modules/group-add.html',{'form': form})
	else:
		form = GroupForm()
		return render(request, 'mophy/modules/group-add.html',{'form': form})
	
@login_required(login_url='mophy:login')
@permission_required('create_role', raise_exception=True)
def add_admin_roles(request):
	try:
		context = {}
		notifications_data = notifications(request)
		context.update(notifications_data)
		modules = list(permission.objects.filter(name="view").values('name','codename','id'))
		if not modules:
			mod = ['create','view','edit','delete']
			modules = list(settings.PERMISSION_MODULES)
			for x in modules:
				for m in mod:
					if not is_obj_exists(permission, {'codename':m+"_"+str(x).replace(" ","_").lower(), 'name':m}):
						permission.objects.create(codename=m+"_"+str(x).replace(" ","_").lower(), name=m)
			modules = list(permission.objects.filter(name="view").values('name','codename','id'))
		for x in modules:
			x['codename'] = str(str(x['codename']).replace(str(x['name']+"_"),"")).replace("_"," ").capitalize()
		modules = [str(m['codename']).title() for m in modules]
		context.update(modules= modules ,permissions= list(permission.objects.all().values('name', 'id')))
		if request.method == 'POST':
			role = request.POST.get('role')
			array = json.loads(request.POST.get('array'))
			if roles.objects.filter(name=str(role).capitalize()).exists():
				return JsonResponse({'success':False, 'message': "Role Name already exists!"})
			if len(array) == 0:
				return JsonResponse({'success':False, 'message': "Please select permissions."})
			role_id = roles.objects.create(name=str(role).lower())
			for a in array:
				codename = str(a['module']).replace(" ","_").lower()
				a['permissions'].pop(a['permissions'].index(str(a['permissions'][0])))
				for nm in a['permissions']:
					if not permission.objects.filter(codename=str(str(nm).lower()+"_"+codename).lower()).exists():
						p_id = permission.objects.create(codename=str(str(nm).lower()+"_"+codename).lower(), name=str(nm).lower())
						role_permissions.objects.create(role_id=role_id.id, permission_id=p_id.id[0]['id'], delete=False)
					else:
						permission_id = permission.objects.filter(codename=str(str(nm).lower()+"_"+codename).lower()).values('id')
						role_permissions.objects.create(role_id=role_id.id, permission_id=permission_id[0]['id'], delete=False)
			return JsonResponse({'success':True, 'redirect_url':str(settings.BASE_URL)+"/adminpanel/roles", 'message': str(role).capitalize()+" role is created succesfully."})
		else:
			return render(request, 'mophy/modules/add_admin_roles.html', context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

@login_required(login_url='mophy:login')
@permission_required('view_role', raise_exception=True)
def roles_list(request):
	try:
		context = {}
		notifications_data = notifications(request)
		context.update(notifications_data)
		data = list(roles.objects.all().values('id','name').order_by('-id'))
		for i in data:
			i.update(user_count = admin_roles.objects.filter(role_id=i['id']).count(),
			perms_count = role_permissions.objects.filter(role_id=i['id'], delete=False).count())
		search_values = [item['id'] for item in data]	
		context.update(data = data)
		return render(request, 'mophy/modules/roles_list.html', context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
@login_required(login_url='mophy:login')
@permission_required('delete_role', raise_exception=True)
def role_delete(request,id):
	try:
		context = {}
		notifications_data = notifications(request)
		context.update(notifications_data)
		role = get_object_or_404(roles,id=id)
		if str(role.name).lower() == "admin":
			messages.warning(request, "You can't delet Admin Role.")
			return redirect('mophy:roles')
		role.delete()
		messages.success(request, str(role.name).capitalize()+' Role Deleted Sucessfully')
		return redirect('mophy:roles')
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False


@login_required(login_url='mophy:login')
@permission_required('edit_role', raise_exception=True)
def edit_role(request,id):	
	try:
		context = {}
		notifications_data = notifications(request)
		context.update(notifications_data)
		previous_permissions = None
		data = None
		modules = list(permission.objects.filter(name="view").values('name','codename','id'))
		for x in modules:
			x['codename'] = str(str(x['codename']).replace(str(str(x['name']).lower()+"_"),"")).replace("_"," ").capitalize()
		modules = [str(m['codename']).title() for m in modules]
		role_obj = get_object_or_404(roles, id=id)
		#getting role permissions
		if role_permissions.objects.filter(role_id=id).exists():
			data = role_permissions.objects.filter(role_id=id, delete=False).values('role_id__name','permission_id__name','permission_id__codename','permission_id')
			previous_permissions = [item['permission_id'] for item in data] #role permissions
			for x in data:
				#updating assigned role permissions codename after modifications
				code = str(str(x['permission_id__codename']).replace(str(x['permission_id__name'])+"_","")).replace("_"," ")
				x.update(codename = code.title(), name= str(x['permission_id__name']).lower())
				#removing existing module name as codename from all modules list || modules are unchecked check boxes for html file and data codenames are checked boxes
				if x['codename'] in modules:
					modules.remove(x['codename'])
			context.update(role_id=id, modules=modules,  data = list(data), role_name = role_obj.name)
		else:
			context.update(role_id=id, modules=modules, role_name = role_obj.name)
		new_list = []
		result_list = []
		if data is not None:
			for item in data:
				module_key = item['codename']
				permission_value = item['permission_id__name']
				existing_module = next((d for d in result_list if d['module'] == module_key), None)
				if existing_module:
					existing_module['permissions'].append(permission_value)
				else:
					new_module_dict = {'module': module_key, 'permissions': [permission_value]}
					result_list.append(new_module_dict)
			context.update(result = result_list)
		if request.method == 'POST':
			role = request.POST.get('role')
			array = json.loads(request.POST.get('array'))
			#getting all selected permissions codename in new_list
			for x in array:
				for z in x['permissions']:
					if x['module'] != z:
						replace_val = str(z).lower()+"_"+str(x['module']).lower()
						new_list.append(replace_val.replace(" ","_").lower())
			#fetching ids of permissions with codename
			permission_ids_data = permission.objects.filter(codename__in=new_list).values('id')
			permission_ids = [item['id'] for item in permission_ids_data]
			for perm in permission_ids:
				#if permission id from selected permissions does not exists in role permissions table then creating new permission for role
				if not role_permissions.objects.filter(role_id=id, permission_id=perm).exists():
					role_permissions.objects.create(role_id=id, permission_id=perm)
				else:
					role_permissions.objects.filter(role_id=id, permission_id=perm).update(delete=False)
			if previous_permissions != None:
				for d in previous_permissions:
					if not d in permission_ids:
						role_permissions.objects.filter(role_id=id, permission_id=d).update(delete=True)
			if data is not None:
				for dic in data:
					if dic['permission_id'] in permission_ids:
						a = str(dic['permission_id__codename']).replace(dic['permission_id__name']+"_", "").replace("_"," ").title()
						if a in list(modules):
							modules.remove(a)
				context['data'] = data
			return JsonResponse({'success':True, 'redirect_url':settings.BASE_URL+"/adminpanel/roles"})
		else:
			return render(request, 'mophy/modules/edit_role.html', context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
@login_required(login_url='mophy:login')
@permission_required('delete_loyality_program', raise_exception=True)
def delete_referral(request,id):
	try:
		context = {}
		notifications_data = notifications(request)
		context.update(notifications_data)
		r =  get_object_or_404(referral, id=id)
		r.delete()
		messages.success(request,'Loyality Program Deleted Sucessfully')
		return redirect('mophy:admin-users')
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
@login_required(login_url='mophy:login')
@permission_required('edit_loyality_program', raise_exception=True)
def edit_referral(request,id):	
	try:
		context = {}
		notifications_data = notifications(request)
		context.update(notifications_data)
		modules = list(permission.objects.filter(name="view").values('name','codename','id'))
		for x in modules:
			x['codename'] = str(str(x['codename']).replace(str(x['name']+"_"),"")).replace("_"," ").capitalize()
		modules = [m['codename'] for m in modules]
		return render(request, 'mophy/modules/edit_role.html', context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
#############################################################

""" Get WidophRemit Accounts List """	
def getRAbankAccounts(zai_user_id):
	try:
		bank_list = []
		bank_list = list(zai_admin_users.objects.all().values())
		if not bank_list:
			bank_list = list(settings.ZAI_ADMIN_USERS)

		#inserting default bank at 0 index
		for s in bank_list:
			if str(s['zai_user_id']) == str(zai_user_id):
				s_index = bank_list.index(s)
				bank_list.pop(s_index)
				bank_list.insert(0, {'bank_name': s['bank_name'], 'zai_user_id':s['zai_user_id'], 'zai_email':s['zai_email']})
		return bank_list
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
""" Get zai wallet balance with id """
@login_required(login_url='mophy:login')
@permission_required('view_zai', raise_exception=True)
def ZaiWalletBalance(request):
	try:	
		if request.method == "POST":
			zai_user_id = request.POST.get('zai_user_id')
			if zai_user_id:
				response = get_RA_zai_wallet(zai_user_id=zai_user_id, request=request)
				balance = comma_value(int(response['wallet_accounts']['balance']) / 100)
				return JsonResponse({'success':True, 'balance':balance})
		return JsonResponse({'success':False})
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
""" New Zai Page """
@login_required(login_url='mophy:login')
def new_zai_page(request):
	try:
		context = context_data(request)	
		#default zai remitassure bank account
		zai_user_id = settings.ZAI_REMIT_USER_ID
		#get default wallet balance
		wallet = get_wallet_balance(zai_user_id=zai_user_id, request=request)

		if request.method == "POST":
			bank_list = getRAbankAccounts(zai_user_id)
			return JsonResponse({'success':True, 'bank_list':bank_list, 'balance':wallet['wallet_balance']})

		#fetching withdraw data history
		withdraw_data = withdraw_zai_funds.objects.exclude(type='ra_payout').values().order_by('-id')	
		withdraw_data = data_to_none_str(withdraw_data)
		#RA bank accounts list
		context.update(bank_list = getRAbankAccounts(zai_user_id), default_balance=wallet['wallet_balance'], withdraw_data=withdraw_data)
		return render(request, 'mophy/zai_page.html', context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

""" Search RemitAsure User Wallet """
@login_required(login_url='mophy:login')
def search_ra_wallet(request):
	zai_data = None	
	bank_name = None
	account_name = None
	try:
		if request.method == "POST":
			zai_user_id = request.POST.get('zai_user_id')
			zai_email = request.POST.get('zai_email')
			type = request.POST.get('type')
			
			if zai_email:
				zai_email = str(zai_email).lower()
			#search zai details first from database			
			if zai_user_id and zai_email:
				if zai_admin_users.objects.filter(zai_email=zai_email).exists():
					zai_data = zai_admin_users.objects.filter(zai_email=zai_email).values()[0]
					if zai_user_id != zai_data['zai_user_id']:
						return JsonResponse({'success':False, 'message':"User ID and Email does not match!"})
				elif zai_admin_users.objects.filter(zai_user_id=zai_user_id).exists():
					zai_data = zai_admin_users.objects.filter(zai_user_id=zai_user_id).values()[0]
					if zai_email != zai_data['zai_email']:
						return JsonResponse({'success':False, 'message':"User ID and Email does not match!"})

			elif zai_user_id and zai_admin_users.objects.filter(zai_user_id=zai_user_id).exists():
				zai_data = zai_admin_users.objects.filter(zai_user_id=zai_user_id).values()[0]
			elif zai_email and zai_admin_users.objects.filter(zai_email=zai_email).exists():
				zai_data = zai_admin_users.objects.filter(zai_email=zai_email).values()[0]

			if zai_data:
				bank_name = zai_data['bank_name']
				zai_email = zai_data['zai_email']
				zai_user_id = zai_data['zai_user_id']
			else:
				if zai_user_id and zai_email:
					#get email with user id
					admin_zai_email = next((i['zai_email'] for i in ZAI_ADMIN_USERS if i['zai_user_id'] == zai_user_id), None)
					admin_zai_user_id = next((i['zai_user_id'] for i in ZAI_ADMIN_USERS if i['zai_email'] == zai_email), None)
					# if both email and user id not foud in admin users
					if not admin_zai_user_id and not admin_zai_email:
						return JsonResponse({'success':False, 'message':"User not Found"})
					
					#if email found with id but email does not match with input email
					if admin_zai_email and zai_email != admin_zai_email:
						return JsonResponse({'success':False, 'message':"User ID and Email does not match!"})
					#if user id found with email but user id does not match with input user id
					elif admin_zai_user_id and zai_user_id != admin_zai_user_id:
						return JsonResponse({'success':False, 'message':"User ID and Email does not match!"})
				elif zai_user_id:
					zai_email = next((i['zai_email'] for i in ZAI_ADMIN_USERS if i['zai_user_id'] == zai_user_id), None)
				else:
					zai_user_id = next((i['zai_user_id'] for i in ZAI_ADMIN_USERS if i['zai_email'] == zai_email), None)
			if zai_user_id and zai_email:
				bank_name, account_name = GetBankName(request, zai_user_id)
				#get balance
				balance_response = get_wallet_balance(zai_user_id, request)
				return JsonResponse({'success':True, 'balance':comma_value(balance_response['wallet_balance']), 'email':zai_email, 'zai_user_id':zai_user_id, 'bank_name':bank_name, 'account_name':account_name})
			else:
				return JsonResponse({'success':False, 'message':"User not Found"})
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return JsonResponse({'success':False, 'message':"User not Found"})

""" Withdraw Zai Funds (New Page)"""
@login_required(login_url='mophy:login')
@permission_required('view_zai', raise_exception=True)
def Withdraw_Funds(request):	
	try:
		context = context_data(request)	
		if request.method == 'POST':		
			zai_user_id = request.POST.get('zai_user_id')
			amount = request.POST.get('amount')	
		
			#get wallet balance
			if zai_user_id and amount:
				wallet_data =  get_wallet_balance(zai_user_id=zai_user_id, request=request)	
				if float(replace_comma(amount)) > float(replace_comma(wallet_data['wallet_balance'])):
					return JsonResponse({'success':False,'message':"Insufficient Balance"})
				
				#withdraw amount
				withdraw_data = withdraw_amount(zai_user_id, amount, request, wallet_data['wallet_id'], wallet_data['wallet_balance'])
				if 'errors' in withdraw_data['response']:
					return JsonResponse({'success':False,'message':withdraw_data['response']['errors']	})		
				return JsonResponse({'success':True,'message':"Funds withdrawn successfully.",'balance': comma_value(withdraw_data['new_balance']),'zai_email':wallet_data['zai_email']})
		return redirect('zai-page')
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

""" Search User Wallets """
@login_required(login_url='mophy:login')
def search_user_wallet(request):
	zai_data = None	
	zai_user_id = None
	try:
		if request.method == "POST":
			zai_user_id = request.POST.get('zai_user_id')
			zai_email = request.POST.get('zai_email')
			
			if zai_email:
				zai_email = str(zai_email).lower()

			#search zai details first from database
			if zai_user_id and zai_email:
				#check input email with database email 
				if zai_payid_details.objects.filter(zai_user_id=zai_user_id).exists():
					zai_data = zai_payid_details.objects.filter(zai_user_id=zai_user_id).values()[0]			
				elif zai_agreement_details.objects.filter(zai_user_id=zai_user_id).exists():
					zai_data = zai_agreement_details.objects.filter(zai_user_id=zai_user_id).values()[0]
				if zai_data and zai_email != zai_data['zai_email']:
					return JsonResponse({'success':False, 'message':"User ID and Email does not match!"})

				#check input user id with database user id 
				if zai_payid_details.objects.filter(zai_email=zai_email).exists():
					zai_data = zai_payid_details.objects.filter(zai_email=zai_email).values()[0]			
				elif zai_agreement_details.objects.filter(zai_email=zai_email).exists():
					zai_data = zai_agreement_details.objects.filter(zai_email=zai_email).values()[0]
				if zai_data and zai_user_id != zai_data['zai_user_id']:
					return JsonResponse({'success':False, 'message':"User ID and Email does not match!"})
				
			elif zai_user_id:
				if zai_payid_details.objects.filter(zai_user_id=zai_user_id).exists():
					zai_data = zai_payid_details.objects.filter(zai_user_id=zai_user_id).values()[0]
				elif zai_agreement_details.objects.filter(zai_user_id=zai_user_id).exists():
					zai_data = zai_agreement_details.objects.filter(zai_user_id=zai_user_id).values()[0]		
			elif zai_email:
				if zai_payid_details.objects.filter(zai_email=zai_email).exists():
					zai_data = zai_payid_details.objects.filter(zai_email=zai_email).values()[0]
				elif zai_agreement_details.objects.filter(zai_email=zai_email).exists():
					zai_data = zai_agreement_details.objects.filter(zai_email=zai_email).values()[0]
			if zai_data:
				zai_user_id = zai_data['zai_user_id']
				zai_email = zai_data['zai_email']
			if zai_email and not zai_data:
				response = zai_search_email_id(zai_token(request), zai_email)
				if 'users' in response:
					for u in response['users']:
						if u['email'] == zai_email:
							if zai_user_id and u['id'] != zai_user_id:
								return JsonResponse({'success':False, 'message':"User ID and Email does not match!"})
							zai_user_id = u['id']
						else:
							return JsonResponse({'success':False, 'message':"User not found"})
				else:
					return JsonResponse({'success':False, 'message':"Invalid email address"})
			elif zai_user_id and not zai_email:
				return JsonResponse({'success':False, 'message':"User not Found with User Id. Please try again with user email."})
			if zai_user_id:		
				#get balance
				balance_response = get_wallet_balance(zai_user_id, request)
				return JsonResponse({'success':True, 'balance': comma_value(balance_response['wallet_balance']), 'email':zai_email, 'zai_user_id':zai_user_id})
			return JsonResponse({'success':False, 'message':"User not Found"})
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return JsonResponse({'success':False, 'message':"User not Found"})

""" Transfer Funds """
@login_required(login_url='mophy:login')
def transfer_funds(request):	
	try:
		source_balance = None
		destination_balance = None
		if request.method == 'POST':		
			destination_id = request.POST.get('destination_id')		
			source_id = request.POST.get('source_id')		
			source_email = request.POST.get('source_email')		
			amount = request.POST.get('amount')		
			item_name = request.POST.get('type')		

			#check blance in source wallet
			if amount and source_id and destination_id:
				if not zai_payid_details.objects.filter(zai_user_id=source_id).exists() and not zai_agreement_details.objects.filter(zai_user_id=source_id).exists():
					if str(item_name).lower() != 'user wallet transfer':
						source_exists = next((True for i in ZAI_ADMIN_USERS if i['zai_user_id'] == source_id), None)
						if not source_exists:
							return JsonResponse({'success':False, 'message':'Invalid source details'})
				source_balance = get_wallet_balance(source_id, request)
				if float(replace_comma(amount)) > float(replace_comma(source_balance['wallet_balance'])):
					return JsonResponse({'success':False, 'message':"Insufficient Balance"})
				
				#transferring funds from one wallet to another
				amount_response = zai_wallet_transfer(source_id, destination_id, amount, request, item_name, source_email )
				if amount_response['code'] == 400:
					return JsonResponse({'success':False, 'message':amount_response['message']})			
				destination_balance = get_wallet_balance(destination_id, request)
				source_balance = get_wallet_balance(source_id, request)
				return JsonResponse({'success':True, 'destination_balance':comma_value(destination_balance['wallet_balance']),'source_balance':comma_value(source_balance['wallet_balance']), 'message':"Funds has been successfully transferred from source walllet to destination wallet."})
			return JsonResponse({'success':False, 'message':'Please check Source and Destination Details'})
		return JsonResponse({'success':False, 'message':'Please check Source and Destination Details'})
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False


############################## Blogs ###############################################
""" Blogs """
@login_required(login_url='mophy:login')
@permission_required('create_blogs', raise_exception=True)
def create_blog(request):
	try:
		if request.method == 'POST':		
			name = request.POST.get('name')		
			short_description = request.POST.get('short_description')		
			description = request.POST.get('description')		
			image = request.FILES.get('image')	
			obj = Blogs.objects.create(name=name, short_description=short_description, description=description)
			obj.image.save(image.name, image, save=True)  
			return JsonResponse({'success':True})
		else:
			context = context_data(request)
			return render(request,'mophy/add_blog.html',context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
""" Blogs Details """
@login_required(login_url='mophy:login')
@permission_required('view_blogs', raise_exception=True)
def blogs_list(request):
	try:
		context = context_data(request)
		data = Blogs.objects.all().values().order_by('id')
		if data:
			context.update(data=data)
		return render(request,'mophy/blogs_list.html',context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	
""" Blogs Details """
@login_required(login_url='mophy:login')
@permission_required('view_blogs', raise_exception=True)
def blog_detail(request, id):
	try:
		data = None
		context = context_data(request)
		if is_obj_exists(Blogs, {'id':id}):
			data = Blogs.objects.filter(id=id).values()[0]
			context.update(data=data)
		return render(request,'mophy/blog_detail.html',context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

@login_required(login_url='mophy:login')
@permission_required('delete_blogs', raise_exception=True)
def delete_blog(request, id):
	try:
		if request.method == 'POST':		
			if is_obj_exists(Blogs, {'id':id}):
				obj = Blogs.objects.filter(id=id)
				obj.delete()
				return JsonResponse({'success':True})
			else:
				return JsonResponse({'success':False})
		else:
			context = context_data(request)
			return redirect('mophy:blogs-list')
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False


############################# Zai Payots ##################################
@login_required(login_url='mophy:login')
@permission_required('create_zai_user', raise_exception=True)
def confirm_details(request):
	try:
		context = context_data(request)
		senders_list = list(zai_admin_users.objects.all().values())
		receivers_list = list(zai_payout_users.objects.all().values())
		if not senders_list:
			senders_list = list(ZAI_ADMIN_USERS)
		if not receivers_list:
			receivers_list = list(ZAI_PAYOUT_USERS)
		context.update(senders_list=senders_list, receivers_list=receivers_list)
		return render(request,'mophy/confirm_details.html',context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

@login_required(login_url='mophy:login')
def zai_ra_payout(request):
	access_token = zai_token(request)
	try:
		if request.method == 'POST':
			sender_id = request.POST.get('sender_id')
			receiver_id = request.POST.get('receiver_id')
			amount = request.POST.get('amount')
			time = timezone.now().time()
			reference_no = "RA"+str(time.second)+str(time.microsecond)

			#get wallet balance
			sender_wallet_respone = zai_get_user_wallet(access_token=access_token, zai_user_id=sender_id)
			if not 'wallet_accounts' in sender_wallet_respone:
				return JsonResponse({'success':False, 'message':'Unable to fetch wallet details of sender'})
			sender_wallet_id = sender_wallet_respone['wallet_accounts']['id'] 
			sender_wallet_blnc = str(sender_wallet_respone['wallet_accounts']['balance'])

			if len(sender_wallet_blnc) == 2:
				sender_wallet_blnc = int(sender_wallet_blnc) / 100.0
			else:
				sender_wallet_blnc = int(sender_wallet_blnc) / 100
			if float(amount) > float(sender_wallet_blnc): 
				return JsonResponse({'success':False, 'message':"Insufficient balance in source wallet account."})
			
			receiver_wallet = get_wallet_balance(zai_user_id=receiver_id, request=request)
			receiver_wallet_id = receiver_wallet['wallet_id']

			#create item
			item_response = zai_create_item(seller_id=receiver_id, access_token=access_token, payment_id=reference_no, amount_reason="WidophRemit Transfer", send_amount=str(amount), zai_user_id=sender_id, send_currency="AUD")
			if 'errors' in item_response:
				return JsonResponse({'success':False, 'message':item_response['errors']})
			payment_response = zai_make_payment(item_id=item_response['items']['id'], wallet_account_id=sender_wallet_id, access_token=zai_token(request))
			if 'errors' in payment_response:
				for key, value in payment_response['errors'].items():
					error = str(value[0])
					return JsonResponse({'success':False, 'message':error})
			
			#withdraw amount to bank
			withdraw_response = withdraw_payout_amount(access_token, receiver_id, amount, request, receiver_wallet_id)
			if 'errors' in withdraw_response:
				if HOST != 'LIVE':
					v_response = verify_zai_user(access_token, str(receiver_id).strip())
					withdraw_response = withdraw_payout_amount(access_token, receiver_id, amount, request, receiver_wallet_id)
					if 'errors' in withdraw_response:
						for key, value in withdraw_response['errors'].items():
							error = str(value[0])
							return JsonResponse({'success':False, 'message':error})
			if zai_payout_users.objects.filter(zai_user_id=receiver_id).exists():				
				destination_bank = zai_payout_users.objects.filter(zai_user_id=receiver_id).values('bank_name')
				destination_bankname = destination_bank[0]['bank_name']
			else:
				for user in ZAI_PAYOUT_USERS:
					if user['zai_user_id'] == receiver_id:
						destination_bankname = user['bank_name']
			receiver_wallet = get_wallet_balance(zai_user_id=receiver_id, request=request)
			withdraw_zai_funds.objects.create(type="ra_payout", source_id=sender_id, receiver_id=receiver_id, destination_id=destination_bankname, wallet_id=sender_wallet_id, status="completed", amount=amount, wallet_balance = comma_value(sender_wallet_blnc), reference_id=reference_no)
			return JsonResponse({'success':True, 'receiver_balance': comma_value(receiver_wallet['wallet_balance']), 'sender_balance': comma_value(sender_wallet_blnc), 'message':"Funds has been tranferred successfully."})
		else:
			return JsonResponse({'success':False, 'message':'Something went wrong'})
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(str(e)+" in line "+str(exc_tb.tb_lineno))
		return JsonResponse({'success':False, 'message':str(e)+" in line "+str(exc_tb.tb_lineno)})

@login_required(login_url='mophy:login')
@permission_required('create_zai_user', raise_exception=True)
def add_payout_account(request):
	try:
		access_token = zai_token(request)
		if request.method == 'POST':		
			first_name = str(request.POST.get('first_name')).lower().strip()
			last_name = str(request.POST.get('last_name')).lower().strip()
			nick_name = str(request.POST.get('nick_name')).lower().strip()
			email = str(request.POST.get('email')).lower().strip()
			bank_name = str(request.POST.get('bank_name')).lower().strip()
			account_name = str(request.POST.get('account_name')).lower().strip()
			account_number = str(request.POST.get('account_number')).lower().strip()
			routing_number = str(request.POST.get('routing_number')).lower().strip()
			account_type = str(request.POST.get('account_type')).lower().strip()
			holder_type = str(request.POST.get('holder_type')).lower().strip()

			print(account_name, "account name = = = = = = = =  =")
			if zai_payout_users.objects.filter(zai_email=email, first_name=first_name, last_name=last_name, nick_name=nick_name).exists():
				user_data = zai_payout_users.objects.filter(zai_email=email).values('zai_user_id')[0]
				customer_id = user_data['zai_user_id']
			else:
				customer_id = create_payout_user_id()
				response = create_zai_payout_user(access_token, customer_id, email, first_name, last_name)
				if 'errors' in response:
					error_logs(response)
					return JsonResponse({'success':False, 'message':zai_error(response)})
				
			#verify zai user
			if HOST != 'LIVE':
				v_response = verify_zai_user(access_token, str(customer_id).strip())
				print(v_response)
				if 'errors' in v_response:
					error_logs(v_response)
				
			bank_response = create_zai_bank_account(access_token, customer_id, bank_name, account_name, account_number, routing_number, account_type, holder_type)
			if 'errors' in bank_response:
				error_logs(bank_response)
				for key, value in bank_response['errors'].items():
					error = str(key)+" "+str(value[0])
					return JsonResponse({'success':False, 'message':error})
			if not zai_payout_users.objects.filter(zai_user_id=customer_id).exists():
				zai_payout_users.objects.create(zai_user_id=customer_id, first_name=first_name, last_name=last_name, zai_email=email, nick_name=nick_name, bank_name=bank_name, account_name=account_name, account_number=account_number, routing_number=routing_number, bank_id=bank_response['bank_accounts']['id'])
			else:
				zai_payout_users.objects.filter(zai_user_id=customer_id).update(first_name=first_name, last_name=last_name, zai_email=email, nick_name=nick_name, bank_name=bank_name, account_name=account_name, account_number=account_number, routing_number=routing_number, bank_id=bank_response['bank_accounts']['id'])
			return JsonResponse({'success':True})
		else:
			context = context_data(request)
			return render(request,'mophy/add_payout_account.html',context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	

@login_required(login_url='mophy:login')
@permission_required('create_zai_user', raise_exception=True)
def edit_payout_account(request, id):
	try:
		access_token = zai_token(request)
		if request.method == 'POST':		
			first_name = request.POST.get('first_name')
			last_name = request.POST.get('last_name')
			nick_name = request.POST.get('nick_name')
			email = request.POST.get('email')		
			if not zai_payout_users.objects.filter(zai_user_id=id).exists():
				return JsonResponse({'success':False, 'message':'User does not exists!'})	
			response = edit_zai_payout_user(access_token, id, email, first_name, last_name)
			if 'errors' in response:
				return JsonResponse({'success':False, 'message':zai_error(response)})			
			zai_payout_users.objects.filter(zai_user_id=id).update(first_name=first_name, last_name=last_name, zai_email=email, nick_name=nick_name, updated_at=get_current_datetime())
			return JsonResponse({'success':True})
		else:
			context = context_data(request)
			data = zai_payout_users.objects.filter(zai_user_id=id).values()[0]
			context.update(user=data, id=id)
			return render(request,'mophy/edit_payout_user.html',context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False
	

@login_required(login_url='mophy:login')
@permission_required('create_zai_user', raise_exception=True)
def link_bank_account(request):
	try:
		access_token = zai_token(request)
		if request.method == 'POST':		
			data = {
                'bank_name': request.POST.get('bank_name'),
                'account_name': request.POST.get('account_name'),
                'routing_number': request.POST.get('routing_number'),
                'account_number': request.POST.get('account_number'),
                'account_type': request.POST.get('account_type'),
                'holder_type': request.POST.get('holder_type'),
                'zai_user_id': request.POST.get('zai_user_id')
            }
			print(data['zai_user_id'], 35555555555555555555555)
			response = create_zai_bank_account(access_token, data['zai_user_id'], data)
			print(response, "========")
			if 'errors' in response:
				return JsonResponse({'success':False, 'message':'Something went wrong'})
			print(response, "====== bank response  ")
			if zai_payout_users.objects.filter(zai_user_id=data['zai_user_id']).exists():
				zai_payout_users.objects.filter(zai_user_id=data['zai_user_id']).update(bank_name=data['bank_name'], account_name=data['account_name'], account_number=data['account_number'], routing_number=data['routing_number'])
			return JsonResponse({'success':True})
		else:
			receivers_list = list(zai_payout_users.objects.all().values())
			if not receivers_list:
				receivers_list = list(ZAI_PAYOUT_USERS)
			context = context_data(request)
			context.update(receivers_list=receivers_list)
		return render(request,'mophy/link_bank_account.html',context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

@login_required(login_url='mophy:login')
@permission_required('create_zai_user', raise_exception=True)
def payout_accounts_list(request):
	try:
		context = context_data(request)
		accounts_list = list(zai_payout_users.objects.all().values())
		if not accounts_list:
			accounts_list = list(ZAI_PAYOUT_USERS)
		context.update(accounts_list=accounts_list)
		return render(request,'mophy/zai_payout_accounts.html',context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

@login_required(login_url='mophy:login')
@permission_required('create_zai_user', raise_exception=True)
def payout_transactions(request, id):
	try:
		context = context_data(request)
		if zai_payout_users.objects.filter(zai_user_id=id).exists():
			data = zai_payout_users.objects.filter(zai_user_id=id).values()[0]
		transactions = withdraw_zai_funds.objects.filter(receiver_id=id, type='ra_payout').values()
		response = get_RA_zai_wallet(zai_user_id=id, request=request)
		if 'errors' in response:
			return JsonResponse({'success':False})
		wallet_balance = comma_value(int(response['wallet_accounts']['balance']) / 100)
		context.update(transactions=transactions, balance=wallet_balance, id=id, data=data)
		return render(request,'mophy/payout_transactions.html',context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False


@login_required(login_url='mophy:login')
def get_payout_wallet_balance(request):
	try:
		if request.method == 'POST':	
			zai_user_id = request.POST.get('zai_user_id')	
			response = get_RA_zai_wallet(zai_user_id=zai_user_id, request=request)
			if 'errors' in response:
				return JsonResponse({'success':False})
			wallet_balance = comma_value(int(response['wallet_accounts']['balance']) / 100)
			wallet_id = response['wallet_accounts']['id']
			return JsonResponse({'success':True, 'balance':wallet_balance})
		else:
			context = context_data(request)
			accounts_list = list(zai_payout_users.objects.all().values())
			if not accounts_list:
				accounts_list = list(ZAI_PAYOUT_USERS)
			context.update(accounts_list=accounts_list)
			return render(request,'mophy/zai_payout_accounts.html',context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return False

from django.core.files.base import ContentFile

################################################### AUSTRAC #################################################
""" Submit Austrac Reports """
# @login_required(login_url='mophy:login')
# @permission_required('view_transaction', raise_exception=True)
# def austrac(request):
# 	try:
# 		if request.method == 'POST':	
# 			id = int(request.POST.get('id'))
# 			xml_type = request.POST.get('type')
# 			print(xml_type, "xml_type")
# 			if not Transaction_details.objects.filter(id=id).exists():
# 				return JsonResponse({'success':False, 'message':'Transaction details not found'})
# 			if austrac_reports.objects.filter(transaction_id=id, type=xml_type, status='submitted').exists():
# 				return JsonResponse({'success':False, 'message':'Report is already submitted'})
# 			data = Transaction_details.objects.filter(id=id).values()[0]
# 			if austrac_reports.objects.filter(transaction_id=id, type=xml_type).exists():
# 				obj = austrac_reports.objects.get(transaction_id=id, type=xml_type)
# 			else:
# 				obj = austrac_reports.objects.create(transaction_id=id, type=xml_type)
# 			filename = str(create_ifti_filename(id))

# 			xml_content, file_name = create_austrac_xml_file(data, obj.id, filename)	
# 			obj.file.save(file_name, ContentFile(xml_content))
# 			obj.type = xml_type  
# 			obj.filename = filename  
# 			obj.save()	
# 			response = submit_report(file_name)	
# 			if response:
# 				austrac_reports.objects.filter(transaction_id=id, type=xml_type).update(status='submitted')
# 			return JsonResponse({'success':True})
# 		else:
# 			context = context_data(request)
# 			array = []
# 			transaction_data = Transaction_details.objects.filter(Q(payment_status=transaction['pending_review']) | Q(payment_status=transaction['completed'])).order_by('-updated_at')
# 			if transaction_data:
# 				transaction_serializer = Transaction_details_web_Serializer(transaction_data, many=True)
# 				for i in list(transaction_serializer.data):
# 					i = dict(i)
# 					i['inflow_status'] = 'pending'
# 					i['outflow_status'] = 'pending'
# 					i['inflow_path'] = None
# 					i['outflow_path'] = None
# 					i['amount'] = comma_value(i['amount'])
# 					i['receive_amount'] = comma_value(i['receive_amount'])
# 					if str(i['total_amount']) == "0.0000" or i['total_amount'] == None or str(i['total_amount']).strip() == '':
# 						i['total_amount'] = comma_value(i['amount'])
# 					else:
# 						i['total_amount'] = comma_value(i['total_amount'])
# 					i['discount_amount'] = comma_value(i['discount_amount'])
# 					if austrac_reports.objects.filter(transaction_id=i['id'], type='inflow').exists():
# 						inflow_data = austrac_reports.objects.filter(transaction_id=i['id'], type='inflow').values()[0]
# 						i['inflow_status'] = inflow_data['status']
# 						i['inflow_path'] = inflow_data['path']
# 					if austrac_reports.objects.filter(transaction_id=i['id'], type='outflow').exists():
# 						outflow_data = austrac_reports.objects.filter(transaction_id=i['id'], type='outflow').values()[0]
# 						i['outflow_status'] = outflow_data['status']
# 						i['outflow_path'] = outflow_data['path']
# 					array.append(i)
# 			context.update(transaction=array, title= "Transaction History")
# 			return render(request,'mophy/austrac.html',context)
# 	except Exception as e:
# 		exc_type, exc_obj, exc_tb = sys.exc_info()
# 		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
# 		error_logs(file_content)
# 		return JsonResponse({'success':False, 'message':'something went wrong'})


@login_required(login_url='mophy:login')
@permission_required('view_transaction', raise_exception=True)
def austrac(request):
	obj = None
	try:
		if request.method == 'POST':	
			xml_array = []
			transactions_id = json.loads(request.POST.get('transactions_id'))
			xml_type = request.POST.get('type')

			xml_array = Transaction_details.objects.filter(transaction_id__in=transactions_id).values()

			filename = str(create_ifti_filename())
			xml_content = create_austrac_xml_file(xml_array, filename)	

			for i in transactions_id:	
				austrac_reports.objects.create(transaction_id=i)

				if austrac_reports.objects.filter(transaction_id=i, type=xml_type).exists():
					obj = austrac_reports.objects.filter(transaction_id=i, type=xml_type)					
				else:
					austrac_reports.objects.create(transaction_id=i)
					obj = austrac_reports.objects.filter(transaction_id=i, type=xml_type)	
				if obj:
					obj.file.save(filename, ContentFile(xml_content))
					obj.save()	

			# response = submit_report(filename, type='IFTI')	

			# if response:
			# 	austrac_reports.objects.filter(transaction_id__in=transactions_id, type=xml_type).update(filename=filename, status='submitted')

			return JsonResponse({'success':True})
		else:
			context = context_data(request)
			array = []
			transaction_data = Transaction_details.objects.filter(Q(payment_status=transaction['pending_review']) | Q(payment_status=transaction['completed'])).order_by('-updated_at')
			if transaction_data:
				transaction_serializer = Transaction_details_web_Serializer(transaction_data, many=True)
				for i in list(transaction_serializer.data):
					i = dict(i)
					i['inflow_status'] = 'pending'
					i['outflow_status'] = 'pending'
					i['inflow_path'] = None
					i['outflow_path'] = None
					i['amount'] = comma_value(i['amount'])
					i['receive_amount'] = comma_value(i['receive_amount'])
					if str(i['total_amount']) == "0.0000" or i['total_amount'] == None or str(i['total_amount']).strip() == '':
						i['total_amount'] = comma_value(i['amount'])
					else:
						i['total_amount'] = comma_value(i['total_amount'])
					i['discount_amount'] = comma_value(i['discount_amount'])
					if austrac_reports.objects.filter(transaction_id=i['id'], type='inflow').exists():
						inflow_data = austrac_reports.objects.filter(transaction_id=i['id'], type='inflow').values()[0]
						i['inflow_status'] = inflow_data['status']
						i['inflow_path'] = inflow_data['path']
					if austrac_reports.objects.filter(transaction_id=i['id'], type='outflow').exists():
						outflow_data = austrac_reports.objects.filter(transaction_id=i['id'], type='outflow').values()[0]
						i['outflow_status'] = outflow_data['status']
						i['outflow_path'] = outflow_data['path']
					array.append(i)
			context.update(transaction=array, title= "Transaction History")
			return render(request,'mophy/austrac.html',context)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return JsonResponse({'success':False, 'message':'something went wrong'})

