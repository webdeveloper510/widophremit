from Remit_Assure.package import *
from datetime import datetime
from payment_app.views import *
from payment_app.models import withdraw_zai_funds
from auth_app.models import *
from django.conf import settings
from auth_app.sendsms import send_sms_to_recipient, send_sms
from auth_app.views import *
from .forms import *
from datetime import datetime
from countryinfo import CountryInfo
from auth_app.sendsms import comma_separated
from auth_app.models import *
from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.hashers import make_password
from django.contrib.sessions.models import Session
from django.middleware.csrf import CsrfViewMiddleware
from django.views.decorators.csrf import csrf_protect
from payment_app.models import *
import pandas as pd

transaction =  TRANSACTION

def get_fields(model):
	return [{f.name:None} for f in model._meta.fields]

def data_to_None(data=None):
	if data is not None:
		for entry in data:
			for key, value in dict(entry).items():
				if str(value).strip() == '':
					entry[key] = None
				if str(key) == 'created_at':
					entry[key] = str(str_to_date(value))
				if str(key) == 'updated_at':
					entry[key] = str(str_to_date(value))
				if str(key) == 'date':
					entry[key] = str(str_to_date(value))
				if not 'payment_status' in entry:
					if 'aml' in str(key).lower() and str(value).lower() != "true" and str(value).lower() != "false":
						entry[key] = "Pending"
		return data
	return []

def comma_value(value):
    if str(value).lower() == 'none' or str(value).strip() == "":
        value = 0    
    value = float(str(value).replace(",",""))
    if value > float(1) or value == float(1):
        value = "{0:,.2f}".format(value)
    else:
        value = "{:.4f}".format(value) 
    return value

def items_to_none(data=None):
	if data is not None:
		for key, value in data.items():
			if str(value).strip() == '':
				data[key] = None
			elif str(key) == 'created_at':
				data[key] = str(str_to_date(value))
			elif str(key) == 'updated_at':
				data[key] = str(str_to_date(value))
			elif str(key) == 'date':
				data[key] = str(str_to_date(value))
		return data
	return []

def get_current_date():
	return timezone.now().date()

def transactions_none_str(data=None):
	if data:
		for item in data:
			for key, value in item.items():
				if str(value).strip() == '':
					item[key] = None
				if str(key) == 'updated_at':
					item[key] = str(str_to_date(value))
				if str(key) == 'date':
					item[key] = str(str_to_date(value))
				if str(key) == 'amount':
					item[key] = comma_value(value)
				if str(key) == 'receive_amount':
					item[key] = comma_value(value)
				if str(key) == 'exchange_rate':
					item[key] = comma_value(value)
				if 'aml' in str(key).lower() and value != True and value != False:
					item[key] = "Pending"
		return data
	return []

#filter value of csv key for user and transaction
def csv_filter_values(type, key):
	if str(type).lower() == "customer" or  str(type).lower() == "customers":
		filter_list = CSV_CUSTOMER_FILTER_VALUES
	else:
		filter_list = CSV_TRANSACTION_FILTER_VALUES
	values = next((item[key] for item in filter_list if key in item), None)
	return values

#get filtered key's value of csv user
def get_csv_values(request):
	if request.method == 'POST':		
		#key = request.session.get('csv_key', None)
		key = request.POST.get('csv_key')
		type = request.POST.get('type')
		request.session['csv_key_'+type] = key
		data = csv_filter_values(type, key)
		return JsonResponse({'success':True, "csv_values":data})
	else:
		return JsonResponse({'success':False, "data":None})
	

#set value of filter from user/transations
def set_value(request):
	if request.method == 'POST':
		type = request.POST.get('type')
		key = request.POST.get('key')		
		val = next((item[key] for item in CSV_DB_VALUES_ if key in item), None)
		if val == None:
			val = key
		request.session['csv_db_value_'+type] = val
		request.session['csv_value_'+type] = key
		request.session['changeValue'] = 1
		data = csv_filter_values(type, key)
		return JsonResponse({'success':True})
	else:
		return JsonResponse({'success':False})
	
#changing field values of csv file while fetching all fields
def customize_csv_file_values(data, type):
	try:
		array = []
		if type == "customer" or type == "customers":
			all_csv_fields = settings.USER_CSV_ALL_FIELDS
		else:
			all_csv_fields = settings.TRANSACTION_CSV_ALL_FIELDS

		for item in data:
			new_item = {}
			for fields in all_csv_fields:
				for key, value in fields.items():
					val = next((i[value] for i in CSV_FILE_FIELD_VALUES_ if value in i), None)
					if val:
						for x in val:
							if item[value] in x:
								item_val = x[item[value]]
						item_val = next((x[item[value]] for x in val if item[value] in x), item[value])
						new_item[key] = str(item_val)
					else:
						if str(item[value]).lower() == 'na':
							new_item[key] = "NA"
						if str(item[value]).strip() == '' or item[value] == None:
							new_item[key] = "None"
						else:
							new_item[key] = str(item[value]).title()
					if str(item[value]).lower() == 'na':
						item[value] = "NA"
					if value == "aml_pep_status" and item[value] != True and item[value] != False:
						new_item[key] = "Pending"
					if value == "is_verified" and item[value] != True:
						new_item[key] = "Pending"
					if value == "promo_marketing" and item[value] != True:
						new_item[key] = "Not Opted"
					elif value == "promo_marketing" and item[value] != False:
						new_item[key] = "Opted"
					if value == "customer_id" and str(item[value]) != 'None':
						new_item['Cust ID'] = str(item[value]).upper()
					if value == "receive_amount":
						new_item['Payout Amount'] = str(item['receive_currency']).upper()+" "+comma_value(str(item['receive_amount']))
					if value == "amount":
						new_item['Total Amount'] = str(item['send_currency']).upper()+" "+comma_value(str(item['total_amount']))
						new_item['Payin Amount'] = str(item['send_currency']).upper()+" "+comma_value(str(item['amount']))
						if item['discount_amount'] != None and str(item['discount_amount']) != "0" and str(item['discount_amount']) != 'None':
							new_item['Discount Amount'] = str(item['send_currency']).upper()+" "+comma_value(str(item['discount_amount']))
						else:
							new_item['Discount Amount'] = "None"
			array.append(new_item)	
		return array
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		return print(str(e)+" in line "+str(exc_tb.tb_lineno))

#get data from database using filter csv key and value
def get_csv_user_data(key, value):
	try:
		data = []
		data_list = []
		old_value = value
		#download all user data in csv file
		if key == None and value == None:
			data = User.objects.filter(is_superuser=False).values().order_by('-id')
			data_list = customize_csv_file_values(data, "customer")

		#csv file data with filter value if aml pep status is pending
		elif str(key).lower() == "aml_pep_status" and str(value).lower() == "pending":
			data = User.objects.filter(aml_pep_status__isnull=True, is_superuser=False).values().order_by('-id')
		else:
			filter_dict = {key:value, 'is_superuser':False}
			data = User.objects.filter(**filter_dict).values().order_by('-id')

		#creating csv file fields 
		if data and key != None and value != None:	
			for data_dict in data:
				if isinstance(data_dict ,dict):
					filterdict={
						'Cust ID': str(data_dict["customer_id"]),
						'Email':data_dict["email"],
						'Mobile':data_dict["mobile"],
					}
					if key != None and value != None:
						if key == 'is_verified':
							new_key = 'Email Verification'
						if key == 'is_digital_Id_verified':
							new_key = 'KYC Status'
						else:
							new_key = str(key).replace("_"," ").title()
						val = next((i[key] for i in CSV_FILE_FIELD_VALUES_ if key in i), None)
						if val:
							item_val = next((x[old_value] for x in val if old_value in x), None)
							filterdict[new_key] = item_val
						else:
							filterdict[new_key] = old_value
					data_list.append(filterdict)
		if not data:
			data_list=[{'Cust ID':None,'Email':None,'Mobile':None}]
		return {'data_list':data_to_None(data_list),'data': data}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		return print(str(e)+" in line "+str(exc_tb.tb_lineno))

#get data from database using filter csv key and value
def get_csv_transaction_data(key, value):
	try:
		data_list = []
		old_value = value
		if key == None and value == None:
			data = Transaction_details.objects.all().values().order_by('-updated_at')
			transaction_csv_fields = settings.TRANSACTION_CSV_ALL_FIELDS
			data_list = customize_csv_file_values(data, "transactions")			
		elif str(key).lower() == "aml_pep_status" and str(value).lower() == "pending":
			data = Transaction_details.objects.filter(aml_pep_status__isnull=True).values().order_by('-updated_at')
		else:
			# if str(key).lower() == "send_method":
			# 	value = next((item[value] for item in CSV_DB_VALUES_ if value in item), None)				
			data = Transaction_details.objects.filter(**{key:value}).values().order_by('-updated_at')
		if data and key != None and value != None:	
			data_list = customize_csv_file_values(data, "transaction")
			# for x in data:
			# 	if isinstance(x ,dict):				
			# 		if str(x['send_method']) == ZAI['payid']:
			# 			send_method = "Zai PayID"
			# 		elif str(x['send_method']) == ZAI['payto']:
			# 			send_method = "Zai PayTo"
			# 		else:
			# 			send_method = str(x['send_method'])
			# 		filterdict={
			# 			'Transaction ID':x["transaction_id"],
			# 			'Date': x['date'],
			# 			'Cust ID': str(x["customer_id"]).upper(),
			# 			'Payin Amount': str(x['send_currency'])+" "+comma_value(str(x["amount"])),
			# 			'Payout Amount': str(x['receive_currency'])+" "+comma_value(str(x["receive_amount"])),
			# 			'FX': comma_value(str(x['exchange_rate'])),
			# 			'Payin Method': send_method,
			# 			'Payout Partner': str(x['payout_partner']),
			# 			'Payment Status': str(x['payment_status']),
			# 			'TM Status': str(x['tm_status']),
			# 		}
			# 		if key != None and value != None:
			# 			new_key = str(key).replace("_"," ").title()
			# 			val = next((i[key] for i in CSV_FILE_FIELD_VALUES_ if key in i), None)
			# 			if val:
			# 				item_val = next((x[old_value] for x in val if old_value in x), None)
			# 				filterdict[new_key] = item_val
			# 			else:
			# 				filterdict[new_key] = old_value

			# 			customize_csv_file_values(data, "transaction")
			# 		if str(x['discount_amount']).lower() != "none" and str(x['discount_amount']) != "0" and str(x['discount_amount']) != "0.0000":
			# 			filterdict.update({"Discount Amount": str(x['send_currency'])+" "+comma_value(str(x["discount_amount"]))})
			# 			filterdict.update({"Total Payin Amount" : str(x['send_currency'])+" "+comma_value(str(x["total_amount"]))})
			# 		data_list.append(filterdict)
		if not data:
			data_list=[{'Transaction ID':None,'Date':None,'Cust ID':None,'Payin Amount':None,'Payout Amount':None,'Payin Method':None,'Payout Partner':None,'Payment Status':None,'FX':None}]
		return {'data_list':data_list,'data': data}	
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		return print(str(e)+" in line "+str(exc_tb.tb_lineno))
	
#creating csv from data
def Download_csv(datalist, type=None):
	if datalist:
		if str(type).lower() == "customer" or str(type).lower() == "customers":
			filename = "CUST"+str(get_current_date()).replace("-","")+".csv"
		elif str(type).lower() == "transaction" or str(type).lower() == "transactions":
			filename = "TRANS"+str(get_current_date()).replace("-","")+".csv"
		else:
			filename = str(get_current_date()).replace("-","")+".csv"
		df=pd.DataFrame(datalist,index=None)
		df.to_csv(f'{CSV_DOWNLOAD_PATH}/'+filename ,index=False,  encoding='utf-8')
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = f'attachment; filename="{filename}"'
		with open(f'{CSV_DOWNLOAD_PATH}/'+filename, 'rb') as csv_file:
			response.write(csv_file.read())
		return response
	return False

#if payment status updated to processed then send sms and email to beneficiary and customer
def sending_sms_email_to_customer_recipient(status_data):
	if status_data[0]['recipient'] and str(status_data[0]['recipient']) != '' and Recipient.objects.filter(id=status_data[0]['recipient']).exists():
		recipient_mobile = Recipient.objects.filter(id=status_data[0]['recipient']).values('mobile','country')
		user_email = User.objects.filter(customer_id=status_data[0]['customer_id']).values('email','is_verified','mobile','First_name','Last_name')
		#sending sms to recipient
		mobile = recipient_mobile[0]['mobile']
		country = CountryInfo(str(recipient_mobile[0]['country']).capitalize())
		country_code = country.calling_codes()
		#replacing + sign and country code from mobile
		mobile = str(mobile).replace(country_code[0], "")
		mobile = str(mobile).replace("+","")
		#replacing 0 from mobile
		if str(mobile[0]) == "0":
			mobile = str(mobile[1:])
		#adding + and country code in mobile
		mobile = "+"+str(country_code[0])+str(mobile)
		sms_response = send_sms_to_recipient(recipient_mobile=mobile, data={'email':user_email[0]['email'],'username':str(user_email[0]['First_name'])+" "+str(user_email[0]['Last_name']),'transaction_id':status_data[0]['transaction_id'],'receive_currency':status_data[0]['receive_currency'], 'receive_amount':status_data[0]['receive_amount']})
		#sending email and sms to customer
		email_transaction_receipt(type="payout",transaction_id=status_data[0]['transaction_id'])
		custSmsResponse = send_sms_to_customer(type="recipient" ,data={'transaction_id':status_data[0]['transaction_id'],'send_currency':status_data[0]['send_currency'], 'send_amount':status_data[0]['amount']}, user_mobile=user_email[0]['mobile'])

################################################ Zai Functions ################################################3
""" get zai user details """
def zai_user_details(zai_user_id, request):
	try:
		url = settings.ZAI_URL+"/users/"+zai_user_id
		headers = { 'Accept': 'application/json', 'Authorization': 'Bearer '+zai_token(request)}
		response = requests.request("GET", url, headers=headers)
		response = response.json()
		return response
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(str(e)+" in line "+str(exc_tb.tb_lineno)+" zai_user_details")
		return bad_response("something went wrong")
	
""" get zai email """
def get_zai_user_email(zai_user_id, request):
	zai_email = None
	try:
		if zai_admin_users.objects.filter(zai_user_id=zai_user_id).exists():
			zai_email = zai_admin_users.objects.filter(zai_user_id=zai_user_id).values('zai_email')
			zai_email = zai_email[0]['zai_email']
		else:
			response = zai_user_details(zai_user_id, request)
			if 'users' in response:
				zai_email = response['users']['email']
		return zai_email
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(str(e)+" in line "+str(exc_tb.tb_lineno)+" get_zai_user_email")
		return bad_response("something went wrong")
	
""" get wallet balance of user from zai """
def get_wallet_balance(zai_user_id, request):	
	#wallet balance api from payment app
	response = get_RA_zai_wallet(zai_user_id=zai_user_id, request=request)
	wallet_balance = int(response['wallet_accounts']['balance']) / 100
	wallet_id = response['wallet_accounts']['id']
	#get user email
	email = get_zai_user_email(zai_user_id, request)
	return {'wallet_balance':comma_value(wallet_balance), 'zai_email':email, 'wallet_id':wallet_id}

""" get zai graph data with time """
def zai_graph_time(time):
	current_time = datetime.now()
	result = []
	list = []
	date = []
	payin_volume = []
	payout_volume = []
	type = None
	current_time = datetime.now()
	if str(time) == "1":  # for today
		type = "1"
		for _ in range(10):
			result.append(current_time)
			current_time -= timedelta(hours=1)  
		result.reverse()	
		now = datetime.now()
		total_payin = 0
		total_payout = 0
		for hour in result:
			one_hour_ago = now - timezone.timedelta(hours=1)
			start_time = datetime.now()
			stop_time = start_time - timedelta(hours=2)  
			payin_vol = Transaction_details.objects.filter(Q(payment_status=transaction['pending_review']) | Q(payment_status=transaction['completed']), updated_at__gte=one_hour_ago, updated_at__lte=now, send_method__icontains="zai" ).aggregate(total=Sum('amount'))
			payout_vol = withdraw_zai_funds.objects.filter(created_at__gte=one_hour_ago, created_at__lte=now, type="Payout",).aggregate(total=Sum('amount'))
			now = one_hour_ago
			if payin_vol['total'] == None:
				payin_vol = 0
			else:
				payin_vol = payin_vol['total']  
			if payout_vol['total'] == None:
				payout_vol = 0
			else:
				payout_vol = payout_vol['total'] 
			total_payin += payin_vol 
			total_payout += payout_vol
			payin_volume.append(payin_vol)
			payout_volume.append(payout_vol)
			date.append(current_time)
			hour = hour.strftime('%I %p')		
			list.append(hour)
		payout_volume.reverse()
		payin_volume.reverse()
	elif str(time) == "30":
		total_payin = 0
		total_payout = 0  
		for _ in range(10):
			result.append(current_time)
			current_time -= timedelta(days=3)  
		result.reverse()	
		old_day = 0
		start_date = None
		end_date = None
		for days in result:
			if start_date is None:
				start_date = days - timedelta(days=3)
			if end_date is None:
				end_date = days
			payin_vol = Transaction_details.objects.filter(Q(payment_status=transaction['pending_review']) | Q(payment_status=transaction['completed']), updated_at__date__range=[start_date.date(), end_date.date()], send_method__icontains="zai" ).aggregate(total=Sum('amount'))
			payout_vol = withdraw_zai_funds.objects.filter(type="Payout",date__range=[start_date.date(), end_date.date()]).aggregate(total=Sum('amount'))
			if payin_vol['total'] == None:
				payin_vol = 0
			else:
				payin_vol = payin_vol['total']  
			if payout_vol['total'] == None:
				payout_vol = 0
			else:
				payout_vol = payout_vol['total']  
			total_payin += payin_vol 
			total_payout += payout_vol
			payin_volume.append(payin_vol)
			payout_volume.append(payout_vol)	
			d = str(start_date.strftime('%d %b'))+" - "+str(end_date.strftime('%d %b'))
			list.append(d)
			if end_date.date() == datetime.now().date():
				break
			start_date = end_date + timedelta(days=1)
			end_date = start_date + timedelta(days=3)
			if end_date.date() > timezone.now().date():
				end_date = timezone.now()		
	elif str(time) == "90": 
		total_payin = 0
		total_payout = 0 
		for _ in range(7):
			result.append(current_time)
			current_time -= timedelta(days=13)  
		result.reverse()	
		end_date = None
		start_date = None
		for days in result:
			if start_date is None:
				start_date = days - timedelta(days=13)
			if end_date is None:
				end_date = days
			payin_vol = Transaction_details.objects.filter(Q(payment_status=transaction['pending_review']) | Q(payment_status=transaction['completed']), updated_at__date__range=[start_date.date(), end_date.date()], send_method__icontains="zai" ).aggregate(total=Sum('amount'))
			payout_vol = withdraw_zai_funds.objects.filter(type="Payout",date__range=[start_date.date(), end_date.date()]).aggregate(total=Sum('amount'))
			if payin_vol['total'] == None:
				payin_vol = 0
			else:
				payin_vol = payin_vol['total']  
			if payout_vol['total'] == None:
				payout_vol = 0
			else:
				payout_vol = payout_vol['total']  
			total_payin += payin_vol 
			total_payout += payout_vol
			payin_volume.append(payin_vol)
			payout_volume.append(payout_vol)
			d = str(start_date.strftime('%d %b'))+" - "+str(end_date.strftime('%d %b'))
			list.append(d)
			if end_date.date() == datetime.now().date():
				break
			start_date = end_date + timedelta(days=1)
			end_date = start_date + timedelta(days=13)
			if end_date.date() > timezone.now().date():
				end_date = timezone.now()		
	else:   # for 7 days
		total_payin = 0
		total_payout = 0
		for x in range(7):
			d = datetime.now() - timedelta(days=x)
			# payin_vol = Transaction_details.objects.filter(Q(payment_status=transaction['pending_review']) | Q(payment_status=transaction['completed']), updated_at__date=d.date(), send_method__icontains="zai" ).aggregate(total=Sum('amount'))
			payin_vol = Transaction_details.objects.filter(Q(payment_status=transaction['pending_review']) | Q(payment_status=transaction['completed']),Q(send_method__icontains="zai") | Q(send_method__icontains="Pay"),  updated_at__date=d.date()).aggregate(total=Sum('amount'))
			payout_vol = withdraw_zai_funds.objects.filter(type="Payout", created_at__date=d.date()).aggregate(total=Sum('amount'))
			if payin_vol['total'] == None:
				payin_vol = 0
			else:
				payin_vol = payin_vol['total']  
			if payout_vol['total'] == None:
				payout_vol = 0
			else:
				payout_vol = payout_vol['total']  
			total_payin += payin_vol 
			total_payout += payout_vol
			payin_volume.append(payin_vol)
			payout_volume.append(payout_vol)
			dd = d.date()
			date.append(dd)
			d = d.strftime("%d %b")
			list.append(d)
		list.reverse()
		payout_volume.reverse()
		payin_volume.reverse()
	return {'list':list,'total_payin':total_payin,'total_payout':total_payout, 'date':date, 'payout_volume':payout_volume,'payin_volume':payin_volume,'type':type}

""" get zai graph payin data """
def zai_payin(payin_time):
	today = date.today()  # Get the current date
	payin_volume =[]
	payin_list = zai_graph_time(time = payin_time)
	payin_data = payin_list['list']	
	dict = {}
	dict.update(payin = payin_list['total_payin'], payin_data= payin_list['list'], payin_volume=payin_list['payin_volume'])
	return dict

""" get zai graph payout data """
def zai_payout(graph_time):
	today = date.today()  # Get the current date
	payout_list = zai_graph_time(time = graph_time)
	dict = {}	
	dict.update(total_payout = payout_list['total_payout'], payout_data=payout_list['list'], payout_volume=payout_list['payout_volume'])
	return dict

""" zai graph data for payin and payout """
def get_zai_payin_payout(graph_time, zai_user_id, request):
	dict = {}
	today = get_current_date()

	#zai payin and payout
	payin = zai_payin(graph_time)	
	payout = zai_payout(graph_time)

	dict.update(payout_data = payout['payout_data'], payout_volume= payout['payout_volume'], payin_data = payin['payin_data'], payin_volume= payin['payin_volume'])
	if float(payin['payin']) == float(0):
		pending_payout = float(payout['total_payout'])
	else:
		pending_payout = float(payin['payin']) - float(payout['total_payout'])
	pending_payout = abs(pending_payout)
	total_payin =  math.floor(float(payin['payin']) * 100) / 100
	total_payout =  math.floor(float(payout['total_payout']) * 100) / 100	
	if float(str(pending_payout).replace(",",'')) < 0:
		pending_payout = "0.0000"
	dict.update(payin= comma_value(total_payin),  payout = comma_value(total_payout), pending_payout= comma_value(pending_payout))
	return dict

def get_zai_bank_details(zai_user_id, request):
    url = settings.ZAI_URL+"/users/"+str(zai_user_id)+"/bank_accounts"
    headers = { 'Accept': 'application/json', 'Authorization': 'Bearer '+zai_token(request)}
    response = requests.request("GET", url, headers=headers)
    response = response.json()
    return response

""" create reference number for zai transaction """
def create_zai_reference_number(request):
	random_digits = [str(random.randint(0, 9)) for _ in range(7)]
	random_digits = ''.join(random_digits)
	reference_id = random_digits
	if is_obj_exists(withdraw_zai_funds, {'reference_id':reference_id}):
		reference_id = create_zai_reference_number(request)
	return reference_id

#withdraw funds from zai wallet
def withdraw_amount(zai_user_id, amount, request, wallet_id=None, wallet_balance=None):
	try:
		access_token = zai_token(request)
		status = "pending"

		#if not wallet id then get wallet id 
		if not wallet_id:
			wallet_response = zai_get_user_wallet(access_token=access_token, zai_user_id=str(zai_user_id))
			if 'errors' in wallet_response:
				return bad_response(wallet_response['errors'])  
			wallet_id = wallet_response['wallet_accounts']['id']

		#get bank id of user
		bank_response = get_zai_bank_details(zai_user_id, request)
		if 'errors' in bank_response:
			return bad_response(bank_response['errors'])  
		bank_id = bank_response['bank_accounts']['id']

		#get reference number
		reference_id = create_zai_reference_number(request)

		withdraw_amount = int(amount) * 100
		#withdrawing funds from zai wallet
		url = settings.ZAI_URL+"/wallet_accounts/"+wallet_id+"/withdraw"
		payload = json.dumps({
				"account_id": bank_id,
				"amount": str(withdraw_amount),
				"reference_id": reference_id
			})
		headers = { 'Authorization': 'Bearer '+access_token, 'Content-Type': 'application/json'}
		response = requests.request("POST", url, headers=headers, data=payload)
		response = response.json()

		#get new wallet balance
		if wallet_balance:
			new_balance = float(replace_comma(wallet_balance)) - float(amount)
			status = "completed"
		else:
			wallet_data =  get_wallet_balance(zai_user_id=zai_user_id, request=request)	
			new_balance = wallet_data['wallet_accounts']['balance']
			status = "completed"

		#save withdraw details in db with new balance
		if is_obj_exists(zai_admin_users, {'zai_user_id':zai_user_id}):
			source_data = zai_admin_users.objects.filter(zai_user_id=zai_user_id).values('bank_name')
			source_bank = source_data[0]['bank_name']
		else:
			source_bank = next((user['bank_name'] for user in ZAI_ADMIN_USERS if user['zai_user_id'] == zai_user_id), None)
		create_model_obj(withdraw_zai_funds, {'type':"Payout", 'source_id':source_bank, 'destination_id':"NA", 'status':status,'reference_id':reference_id, 'wallet_id':wallet_id, 'amount':amount, 'wallet_balance':new_balance})
		return {'response':response, 'new_balance':new_balance}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(str(e)+" in line "+str(exc_tb.tb_lineno))
		return bad_response(str(e)+" in line "+str(exc_tb.tb_lineno))

""" Get list of unclaimed rewards """
def unclaimed_rewards(filter_currency, user, id):
	try:
		unclaimed_data = []
		discount_data = referral.objects.filter(status="active", currency=filter_currency, referral_type__type=referral_dict['invite']).values()

		#discount of signup with referral code  (REFERRED BY DISCOUNT)
		data1 = referral_meta.objects.filter(user_id=id, is_used=False, referred_by__isnull=False, referred_to__isnull=True)
		for d in data1:
			if str(discount_data[0]['status']).lower() == "active":
				unclaimed_data.append({'type':d.referral.name, 'amount':filter_currency+" "+str(discount_data[0]['referred_to_amount'])})
		
		#discount coupons for inviting users (REFERRED TO DISCOUNT)
		data2 = referral_meta.objects.filter(user_id=id, is_used=False, referred_by__isnull=True, referred_to__isnull=False)
		for d in data2:
			#checking invited user has completed any transction or not
			referred_to_user = User.objects.filter(id=d.referred_to).values('customer_id')[0]
			if str(discount_data[0]['status']).lower() == "active" and Transaction_details.objects.filter(Q(payment_status=transaction['pending_review']) | Q(payment_status=transaction['completed']), customer_id=referred_to_user['customer_id']).exists():	
				unclaimed_data.append({'type':d.referral.name, 'amount':filter_currency+" "+str(discount_data[0]['referred_by_amount'])})
		
		#update birthday reward in unclaimed if user has not used this year
		if user.Date_of_birth:
			if str_to_date(user.Date_of_birth).month == get_current_date().month:
				bdy_referral_ids = referral.objects.filter(referral_type__type=referral_dict['birthday'])
				#if user has not used bdy voucher in current year
				if not referral_meta.objects.filter(is_used=True,referral_id__in=bdy_referral_ids, user_id=id, claimed_date__year=get_current_date().year).exists():
					bdy_data = referral.objects.filter(status="active", currency=filter_currency, referral_type__type=referral_dict['birthday']).values()
					unclaimed_data.append({'type':bdy_referral_ids[0].name, 'amount':filter_currency+" "+str(bdy_data[0]['referred_by_amount'])})
		
		#get all other unclaimed rewards
		other_data = referral.objects.all()
		for i in other_data:
			if str(i.status).lower() == "active" and str(i.referral_type.type).lower() != str(referral_dict['invite']).lower() and str(i.referral_type.type).lower() != str(referral_dict['birthday']).lower():
				unclaimed_data.append({'type':i.name, 'amount':filter_currency+" "+str(i.referred_by_amount)})
		return unclaimed_data
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(str(e)+" in line "+str(exc_tb.tb_lineno))
		return unclaimed_data

""" Wallet transfer in zai """
def zai_wallet_transfer(source_id, destination_id, amount, request, item_name=None, source_email=None):
	if not item_name:
		item_name = "Wallet Transfer"
	send_amount = int(amount)*100 
	reference_id = str(create_zai_reference_number(request))
	access_token = zai_token(request)    

	#get wallet account id
	wallet_data = get_wallet_balance(source_id, request)
	source_wallet_id = wallet_data['wallet_id']
	source_wallet_balance = wallet_data['wallet_balance']

	#creating item
	url = settings.ZAI_URL+"/items"
	payload = json.dumps({
			"id": str(reference_id), 
			"name": item_name, 
			"amount": str(send_amount), 
			"payment_type": "2",
			"buyer_id": source_id, 
			"seller_id": destination_id, 
			"currency": "AUD" 
		})
	headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Bearer '+access_token }
	item_response = requests.request("POST", url, headers=headers, data=payload)
	item_response = item_response.json()
	if 'errors' in item_response:
		return {'code':"400",'message':item_response['errors']}  
	item_id = item_response['items']['id']

	#make payment
	payment_response = zai_make_payment(item_id, source_wallet_id, access_token)
	if 'errors' in payment_response:
		return {'code':"400",'message':payment_response['errors']}

	#get new wallet balance of source
	new_wallet_data = get_wallet_balance(source_id, request)
	new_source_balance = comma_value(new_wallet_data['wallet_balance'])

	#get bank name of source and destinaton
	source_bank, source_account_name = GetBankName(request, source_id)
	destination_bank = next((i['bank_name'] for i in ZAI_ADMIN_USERS if i['zai_user_id'] == destination_id), None)
	if not source_bank and not source_email:
		source_bank = source_id
	else:
		source_bank = source_email
	if not destination_bank:
		destination_bank, destination_account_name = GetBankName(request, destination_id)
		if not destination_bank:
			destination_bank = destination_id
	id = withdraw_zai_funds.objects.create(type=item_name,amount=amount, source_id=source_bank, destination_id=destination_bank, wallet_id=source_wallet_id, status="completed", reference_id=reference_id, wallet_balance=new_source_balance)
	return {'code':"200",'message':"success", 'id':id.id, 'new_balance':new_source_balance, 'zai_email':wallet_data['zai_email']}

""" Filter pending payments on transaction monitoring page """
def pending_payments_transaction_monitoring(corridor, tm_status):
	try:
		if corridor is None and tm_status is None:
			pending_transactions = Transaction_details.objects.filter(payment_status=transaction['pending_payment']).values()		
		else:
			if corridor == "all":
				pending_transactions = Transaction_details.objects.filter(tm_status=tm_status, payment_status=transaction['pending_payment']).values()
			else:
				pending_transactions = Transaction_details.objects.filter(tm_status=tm_status, receive_currency=corridor,payment_status=transaction['pending_payment']).values()
		return transactions_none_str(pending_transactions)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		return (str(e)+" in line "+str(exc_tb.tb_lineno))

""" Get Bank deatils """
def GetBankName(request, zai_user_id):
	bank_name = None
	account_name = None
	url = ZAI_URL+"/users/"+str(zai_user_id)+"/bank_accounts"
	headers = {	'Authorization': 'Bearer '+zai_token(request)}
	response = requests.request("GET", url, headers=headers)
	if response.status_code == 200:
		response = response.json()
		bank_name = response['bank_accounts']['bank']['bank_name']
		account_name = response['bank_accounts']['bank']['account_name']
	return bank_name, account_name

""" Create Tier Item """
def create_tier(customer_id, old_value, new_value, type):
	try:
		type = str(type).lower()
		if is_obj_exists(Tiers, {'customer_id':customer_id, 'type':type}):
			Tiers.objects.filter(customer_id=customer_id, type=type).update(old_tier=old_value, new_tier=new_value, updated_at=get_current_datetime())
		else:
			Tiers.objects.create(customer_id=customer_id, old_tier=old_value, new_tier=new_value, type=type)
		return True
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ "in line " +str(exc_tb.tb_lineno)+" in users/users_views"
		error_logs(file_content)
		return (str(e)+" in line "+str(exc_tb.tb_lineno))


def create_payout_user_id():
    try:
        length = 6
        random_digits = [str(random.randint(0, 9)) for _ in range(length)]
        random_digits = ''.join(random_digits)
        customer_id = "P"+str(random_digits)
        if zai_payout_users.objects.filter(zai_user_id=customer_id).exists():
            customer_id =  create_customer_id()
        return customer_id
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in auth_app/helpers"
        error_logs(file_content)
        return bad_response(message=str(e)+" in line "+str(exc_tb.tb_lineno))

""" Create user in zai """
def create_zai_payout_user(access_token, customer_id, email, fn, ln):
    try:
        url = settings.ZAI_URL+"/users"
        payload = json.dumps({
            "id":customer_id,
            "first_name": fn,
            "last_name": ln,
            "email": email,
            "country": "AU"
        })
        headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer '+access_token
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in user_views/helpers"
        error_logs(file_content)
        return str(e)+" in line "+str(exc_tb.tb_lineno)  

""" Edit user in zai """
def edit_zai_payout_user(access_token, id, email, fn, ln):
	try:
		url = settings.ZAI_URL+"/users/"+id
		payload = json.dumps({
			"first_name": fn,
			"last_name": ln,
			"email": email
		})
		headers = {
		'Content-Type': 'application/json',
		'Accept': 'application/json',
		'Authorization': 'Bearer '+access_token
		}
		response = requests.request("PATCH", url, headers=headers, data=payload)
		response = response.json()
		return response
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in user_views/helpers"
		error_logs(file_content)
		return str(e)+" in line "+str(exc_tb.tb_lineno)  
	
""" Verify user """
def verify_zai_user(access_token, id):
	try:
		url = settings.ZAI_URL+"/users/"+id+"/identity_verified"
		payload = ""
		headers = {
		'Authorization': 'Bearer '+access_token
		}
		response = requests.request("PATCH", url, headers=headers, data=payload)
		return response.json()
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in user_views/helpers"
		error_logs(file_content)
		return str(e)+" in line "+str(exc_tb.tb_lineno) 
	
def get_zai_user(access_token, id):
    try:
        url = settings.ZAI_URL+"/users/"+id        
        headers = {
			'Content-Type': 'application/json',
			'Accept': 'application/json',
			'Authorization': 'Bearer '+access_token
        }
        response = requests.request("GET", url, headers=headers)
        response = response.json()
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in user_views/helpers"
        error_logs(file_content)
        return str(e)+" in line "+str(exc_tb.tb_lineno) 
	
def withdraw_payout_amount(access_token, zai_user_id, amount, request, wallet_id):
	try:
		#get bank id of user
		bank_response = get_zai_bank_details(zai_user_id, request)
		if 'errors' in bank_response:
			return bad_response(bank_response['errors'])  
		bank_id = bank_response['bank_accounts']['id']

		#get reference number
		reference_id = create_zai_reference_number(request)

		withdraw_amount = int(amount) * 100
		#withdrawing funds from zai wallet
		url = settings.ZAI_URL+"/wallet_accounts/"+wallet_id+"/withdraw"
		payload = json.dumps({
				"account_id": bank_id,
				"amount": str(withdraw_amount),
				"reference_id": reference_id
			})
		headers = { 'Authorization': 'Bearer '+access_token, 'Content-Type': 'application/json'}
		response = requests.request("POST", url, headers=headers, data=payload)
		response = response.json()
		return response
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in user_views/helpers"
		error_logs(file_content)
		return str(e)+" in line "+str(exc_tb.tb_lineno) 

def submit_report(file_name, type):
	try:
		if type == 'IFTI':
			url = AUSTRAC_IFTI_URL
		else:
			url = AUSTRAC_TTR_URL
		path = str(os.getcwd())+"/media/austrac/"+str(file_name)
		payload = {
			'userId': AUSTRAC_USER_ID,
			'password': AUSTRAC_PASSWORD,
			'reNumber': AUSTRAC_RE_NUMBER,
			'version': AUSTRAC_VERSION
		}
		files=[
			('fileName',(file_name,open(path,'rb'),'text/xml'))
		]
		headers = {}
		response = requests.request("POST", url, headers=headers, data=payload, files=files)
		print(response.text)
		return True
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		file_content = str(e)+ " in line " +str(exc_tb.tb_lineno)+" in user_views/helpers"
		error_logs(file_content)
		return False

import xml.etree.ElementTree as ET

def create_ifti_filename():
	current_time = datetime.now()
	date = get_current_date()
	date = str(date).replace("-","")
	formatted = date+str(current_time.strftime("%S")).replace(":","")
	filename = "IFTI-DRA"+str(formatted)+".xml"
	return filename

# def create_austrac_xml_file(data, id, filename):
# 	print(XML_RE_NUMBER, "XML_RE_NUMBER = = =")
# 	try:
# 		# Define the root element with namespace
# 		root = ET.Element("ifti-draList", xmlns="http://austrac.gov.au/schema/reporting/IFTI-DRA-1-2")

# 		# Add child elements with text content
# 		re_number = ET.SubElement(root, "reNumber")
# 		re_number.text = XML_RE_NUMBER

# 		file_name = ET.SubElement(root, "fileName")
# 		file_name.text = filename

# 		report_count = ET.SubElement(root, "reportCount")
# 		report_count.text = "1"

# 		# Create ifti-dra element
# 		ifti_dra = ET.SubElement(root, "ifti-dra", id="ID_1R")

# 		# Add header
# 		header = ET.SubElement(ifti_dra, "header", id="ID_1R01")
# 		txn_ref_no = ET.SubElement(header, "txnRefNo")
# 		txn_ref_no.text = "FTI200904301159"

# 		# Add transaction
# 		transaction = ET.SubElement(ifti_dra, "transaction", id="ID_1R02")
# 		txn_date = ET.SubElement(transaction, "txnDate")
# 		txn_date.text = "2009-04-30"

# 		# Add currency amount
# 		currency_amount = ET.SubElement(transaction, "currencyAmount", id="ID_1R03")
# 		currency = ET.SubElement(currency_amount, "currency")
# 		currency.text = "AUD"
# 		amount = ET.SubElement(currency_amount, "amount")
# 		amount.text = "6250.00"

# 		# Add direction
# 		direction = ET.SubElement(transaction, "direction")
# 		direction.text = "I"

# 		# Add transfer type
# 		tfr_type = ET.SubElement(transaction, "tfrType", id="ID_1R04")
# 		money = ET.SubElement(tfr_type, "money")

# 		# Add value date
# 		value_date = ET.SubElement(transaction, "valueDate")
# 		value_date.text = "2009-05-01"

# 		# Add transferor
# 		transferor = ET.SubElement(ifti_dra, "transferor", id="ID_1R05")
# 		full_name = ET.SubElement(transferor, "fullName")
# 		full_name.text = "John Citizen"
# 		main_address = ET.SubElement(transferor, "mainAddress", id="ID_1R06")
# 		addr = ET.SubElement(main_address, "addr")
# 		addr.text = "99 Hunter Street"
# 		suburb = ET.SubElement(main_address, "suburb")
# 		suburb.text = "Port Moresby"
# 		country = ET.SubElement(main_address, "country")
# 		country.text = "Papua New Guinea"
# 		phone = ET.SubElement(transferor, "phone")
# 		phone.text = "+675 123 4567"

# 		# Add ordering institution
# 		ordering_instn = ET.SubElement(ifti_dra, "orderingInstn", id="ID_1R07")
# 		branch = ET.SubElement(ordering_instn, "branch", id="ID_1R08")
# 		full_name_branch = ET.SubElement(branch, "fullName")
# 		full_name_branch.text = "Kina Xpress.Org"
# 		main_address_branch = ET.SubElement(branch, "mainAddress", id="ID_1R09")
# 		addr_branch = ET.SubElement(main_address_branch, "addr")
# 		addr_branch.text = "Cnr Musgrave Street"
# 		suburb_branch = ET.SubElement(main_address_branch, "suburb")
# 		suburb_branch.text = "Port Moresby"
# 		country_branch = ET.SubElement(main_address_branch, "country")
# 		country_branch.text = "Papua New Guinea"
# 		foreign_based = ET.SubElement(ordering_instn, "foreignBased")
# 		foreign_based.text = "Y"
# 		phone_ordering = ET.SubElement(ordering_instn, "phone")
# 		phone_ordering.text = "+675 765 4321"
# 		email_ordering = ET.SubElement(ordering_instn, "email")
# 		email_ordering.text = "portmoresby@kinaxpress.org.pg"
# 		business_struct = ET.SubElement(ordering_instn, "businessStruct")
# 		business_struct.text = "A"

# 		# Add initiating institution
# 		initiating_instn = ET.SubElement(ifti_dra, "initiatingInstn", id="ID_1R10")
# 		same_as_ordering = ET.SubElement(initiating_instn, "sameAsOrderingInstn")
# 		same_as_ordering.text = "Y"

# 		# Add sending institution
# 		sending_instn = ET.SubElement(ifti_dra, "sendingInstn", id="ID_1R11")
# 		same_as_ordering = ET.SubElement(sending_instn, "sameAsOrderingInstn")
# 		same_as_ordering.text = "Y"

# 		# Add receiving institution
# 		receiving_instn = ET.SubElement(ifti_dra, "receivingInstn", id="ID_1R12")
# 		full_name_receiving = ET.SubElement(receiving_instn, "fullName")
# 		full_name_receiving.text = "OZ Dollar Express Pty Ltd"
# 		main_address_receiving = ET.SubElement(receiving_instn, "mainAddress", id="ID_1R13")
# 		addr_receiving = ET.SubElement(main_address_receiving, "addr")
# 		addr_receiving.text = "1a/199 Mount Street"
# 		suburb_receiving = ET.SubElement(main_address_receiving, "suburb")
# 		suburb_receiving.text = "Coogee"
# 		state_receiving = ET.SubElement(main_address_receiving, "state")
# 		state_receiving.text = "NSW"
# 		postcode_receiving = ET.SubElement(main_address_receiving, "postcode")
# 		postcode_receiving.text = "2034"
# 		country_receiving = ET.SubElement(main_address_receiving, "country")
# 		country_receiving.text = "Australia"

# 		# Add beneficiary institution
# 		beneficiary_instn = ET.SubElement(ifti_dra, "beneficiaryInstn", id="ID_1R14")
# 		full_name_beneficiary = ET.SubElement(beneficiary_instn, "fullName")
# 		full_name_beneficiary.text = "Rockhampton Transfers Pty Ltd"
# 		main_address_beneficiary = ET.SubElement(beneficiary_instn, "mainAddress", id="ID_1R15")
# 		addr_beneficiary = ET.SubElement(main_address_beneficiary, "addr")
# 		addr_beneficiary.text = "Shop 1, 123 Denison Street"
# 		suburb_beneficiary = ET.SubElement(main_address_beneficiary, "suburb")
# 		suburb_beneficiary.text = "Rockhampton"
# 		state_beneficiary = ET.SubElement(main_address_beneficiary, "state")
# 		state_beneficiary.text = "QLD"
# 		postcode_beneficiary = ET.SubElement(main_address_beneficiary, "postcode")
# 		postcode_beneficiary.text = "4700"
# 		country_beneficiary = ET.SubElement(main_address_beneficiary, "country")
# 		country_beneficiary.text = "Australia"

# 		# Add transferee
# 		transferee = ET.SubElement(ifti_dra, "transferee", id="ID_1R16")
# 		full_name_transferee = ET.SubElement(transferee, "fullName")
# 		full_name_transferee.text = "Some Academic Grammar School"
# 		main_address_transferee = ET.SubElement(transferee, "mainAddress", id="ID_1R17")
# 		addr_transferee = ET.SubElement(main_address_transferee, "addr")
# 		addr_transferee.text = "Lennox Street"
# 		suburb_transferee = ET.SubElement(main_address_transferee, "suburb")
# 		suburb_transferee.text = "Rockhampton"
# 		state_transferee = ET.SubElement(main_address_transferee, "state")
# 		state_transferee.text = "QLD"
# 		postcode_transferee = ET.SubElement(main_address_transferee, "postcode")
# 		postcode_transferee.text = "4700"
# 		country_transferee = ET.SubElement(main_address_transferee, "country")
# 		country_transferee.text = "Australia"
# 		phone_transferee = ET.SubElement(transferee, "phone")
# 		phone_transferee.text = "+61 7 4999 9999"
# 		email_transferee = ET.SubElement(transferee, "email")
# 		email_transferee.text = "bursar@iags.qld.edu.au"
# 		account = ET.SubElement(transferee, "account", id="ID_1R18")
# 		acct_number = ET.SubElement(account, "acctNumber")
# 		acct_number.text = "9876543210"
# 		name_account = ET.SubElement(account, "name")
# 		name_account.text = "Major Bank Limited"
# 		city_account = ET.SubElement(account, "city")
# 		city_account.text = "Rockhampton"
# 		country_account = ET.SubElement(account, "country")
# 		country_account.text = "Australia"

# 		# Add additional details
# 		additional_details = ET.SubElement(ifti_dra, "additionalDetails", id="ID_1R19")
# 		reason_for_transfer = ET.SubElement(additional_details, "reasonForTransfer")
# 		reason_for_transfer.text = "A. Citizen - School Fees Term 2"

# 		# Write the tree to an XML file
# 		tree = ET.ElementTree(root)
# 		# tree.write("IFTI-DRA2024080745.xml", encoding="utf-8", xml_declaration=True)
# 		xml_content = ET.tostring(root, encoding='utf-8', method='xml').decode('utf-8')
# 		return xml_content, str(filename)
# 	except Exception as e:
# 		exc_type, exc_obj, exc_tb = sys.exc_info()
# 		print(str(e)+" in line "+str(exc_tb.tb_lineno))
# 		return bad_response(str(e)+" in line "+str(exc_tb.tb_lineno))

def create_austrac_xml_file(array, filename):
	print(XML_RE_NUMBER, "XML_RE_NUMBER = = =")
	try:
		# Define the root element with namespace
		root = ET.Element("ifti-draList", xmlns="http://austrac.gov.au/schema/reporting/IFTI-DRA-1-2")

		# Add child elements with text content
		re_number = ET.SubElement(root, "reNumber")
		re_number.text = XML_RE_NUMBER

		file_name = ET.SubElement(root, "fileName")
		file_name.text = filename

		report_count = ET.SubElement(root, "reportCount")
		report_count.text = str(len(array))

		for idx, item in enumerate(array, start=1):
			# Create ifti-dra element
			ifti_dra = ET.SubElement(root, "ifti-dra", id=f"ID_{idx}R")

			# Add header
			header = ET.SubElement(ifti_dra, "header", id=f"ID_{idx}R01")
			txn_ref_no = ET.SubElement(header, "txnRefNo")
			txn_ref_no.text = item.get('txnRefNo', f"FTI200904301159_{idx}")  

			# Add transaction
			transaction = ET.SubElement(ifti_dra, "transaction", id=f"ID_{idx}R02")
			txn_date = ET.SubElement(transaction, "txnDate")
			txn_date.text = "2009-04-30"

			# Add currency amount
			currency_amount = ET.SubElement(transaction, "currencyAmount", id=f"ID_{idx}R03")
			currency = ET.SubElement(currency_amount, "currency")
			currency.text = "AUD"
			amount = ET.SubElement(currency_amount, "amount")
			amount.text = "6250.00"

			# Add direction
			direction = ET.SubElement(transaction, "direction")
			direction.text = "I"

			# Add transfer type
			tfr_type = ET.SubElement(transaction, "tfrType", id=f"ID_{idx}R04")
			money = ET.SubElement(tfr_type, "money")

			# Add value date
			value_date = ET.SubElement(transaction, "valueDate")
			value_date.text = "2009-05-01"

			# Add transferor
			transferor = ET.SubElement(ifti_dra, "transferor", id=f"ID_{idx}R05")
			full_name = ET.SubElement(transferor, "fullName")
			full_name.text = "John Citizen"
			main_address = ET.SubElement(transferor, "mainAddress", id=f"ID_{idx}R06")
			addr = ET.SubElement(main_address, "addr")
			addr.text = "99 Hunter Street"
			suburb = ET.SubElement(main_address, "suburb")
			suburb.text = "Port Moresby"
			country = ET.SubElement(main_address, "country")
			country.text = "Papua New Guinea"
			phone = ET.SubElement(transferor, "phone")
			phone.text = "+675 123 4567"

			# Add ordering institution
			ordering_instn = ET.SubElement(ifti_dra, "orderingInstn", id=f"ID_{idx}R07")
			branch = ET.SubElement(ordering_instn, "branch", id=f"ID_{idx}R08")
			full_name_branch = ET.SubElement(branch, "fullName")
			full_name_branch.text = "Kina Xpress.Org"
			main_address_branch = ET.SubElement(branch, "mainAddress", id=f"ID_{idx}R09")
			addr_branch = ET.SubElement(main_address_branch, "addr")
			addr_branch.text = "Cnr Musgrave Street"
			suburb_branch = ET.SubElement(main_address_branch, "suburb")
			suburb_branch.text = "Port Moresby"
			country_branch = ET.SubElement(main_address_branch, "country")
			country_branch.text = "Papua New Guinea"
			foreign_based = ET.SubElement(ordering_instn, "foreignBased")
			foreign_based.text = "Y"
			phone_ordering = ET.SubElement(ordering_instn, "phone")
			phone_ordering.text = "+675 765 4321"
			email_ordering = ET.SubElement(ordering_instn, "email")
			email_ordering.text = "portmoresby@kinaxpress.org.pg"
			business_struct = ET.SubElement(ordering_instn, "businessStruct")
			business_struct.text = "A"

			# Add initiating institution
			initiating_instn = ET.SubElement(ifti_dra, "initiatingInstn", id=f"ID_{idx}R10")
			same_as_ordering = ET.SubElement(initiating_instn, "sameAsOrderingInstn")
			same_as_ordering.text = "Y"

			# Add sending institution
			sending_instn = ET.SubElement(ifti_dra, "sendingInstn", id=f"ID_{idx}R11")
			same_as_ordering = ET.SubElement(sending_instn, "sameAsOrderingInstn")
			same_as_ordering.text = "Y"

			# Add receiving institution
			receiving_instn = ET.SubElement(ifti_dra, "receivingInstn", id=f"ID_{idx}R12")
			full_name_receiving = ET.SubElement(receiving_instn, "fullName")
			full_name_receiving.text = "OZ Dollar Express Pty Ltd"
			main_address_receiving = ET.SubElement(receiving_instn, "mainAddress", id=f"ID_{idx}R13")
			addr_receiving = ET.SubElement(main_address_receiving, "addr")
			addr_receiving.text = "1a/199 Mount Street"
			suburb_receiving = ET.SubElement(main_address_receiving, "suburb")
			suburb_receiving.text = "Coogee"
			state_receiving = ET.SubElement(main_address_receiving, "state")
			state_receiving.text = "NSW"
			postcode_receiving = ET.SubElement(main_address_receiving, "postcode")
			postcode_receiving.text = "2034"
			country_receiving = ET.SubElement(main_address_receiving, "country")
			country_receiving.text = "Australia"

			# Add beneficiary institution
			beneficiary_instn = ET.SubElement(ifti_dra, "beneficiaryInstn", id=f"ID_{idx}R14")
			full_name_beneficiary = ET.SubElement(beneficiary_instn, "fullName")
			full_name_beneficiary.text = "Rockhampton Transfers Pty Ltd"
			main_address_beneficiary = ET.SubElement(beneficiary_instn, "mainAddress", id=f"ID_{idx}R15")
			addr_beneficiary = ET.SubElement(main_address_beneficiary, "addr")
			addr_beneficiary.text = "Shop 1, 123 Denison Street"
			suburb_beneficiary = ET.SubElement(main_address_beneficiary, "suburb")
			suburb_beneficiary.text = "Rockhampton"
			state_beneficiary = ET.SubElement(main_address_beneficiary, "state")
			state_beneficiary.text = "QLD"
			postcode_beneficiary = ET.SubElement(main_address_beneficiary, "postcode")
			postcode_beneficiary.text = "4700"
			country_beneficiary = ET.SubElement(main_address_beneficiary, "country")
			country_beneficiary.text = "Australia"

			# Add transferee
			transferee = ET.SubElement(ifti_dra, "transferee", id=f"ID_{idx}R16")
			full_name_transferee = ET.SubElement(transferee, "fullName")
			full_name_transferee.text = "Some Academic Grammar School"
			main_address_transferee = ET.SubElement(transferee, "mainAddress", id=f"ID_{idx}R17")
			addr_transferee = ET.SubElement(main_address_transferee, "addr")
			addr_transferee.text = "Lennox Street"
			suburb_transferee = ET.SubElement(main_address_transferee, "suburb")
			suburb_transferee.text = "Rockhampton"
			state_transferee = ET.SubElement(main_address_transferee, "state")
			state_transferee.text = "QLD"
			postcode_transferee = ET.SubElement(main_address_transferee, "postcode")
			postcode_transferee.text = "4700"
			country_transferee = ET.SubElement(main_address_transferee, "country")
			country_transferee.text = "Australia"
			phone_transferee = ET.SubElement(transferee, "phone")
			phone_transferee.text = "+61 7 4999 9999"
			email_transferee = ET.SubElement(transferee, "email")
			email_transferee.text = "bursar@iags.qld.edu.au"
			account = ET.SubElement(transferee, "account", id=f"ID_{idx}R18")
			acct_number = ET.SubElement(account, "acctNumber")
			acct_number.text = "9876543210"
			name_account = ET.SubElement(account, "name")
			name_account.text = "Major Bank Limited"
			city_account = ET.SubElement(account, "city")
			city_account.text = "Rockhampton"
			country_account = ET.SubElement(account, "country")
			country_account.text = "Australia"

			# Add additional details
			additional_details = ET.SubElement(ifti_dra, "additionalDetails", id=f"ID_{idx}R19")
			reason_for_transfer = ET.SubElement(additional_details, "reasonForTransfer")
			reason_for_transfer.text = "A. Citizen - School Fees Term 2"

		# Write the tree to an XML file
		tree = ET.ElementTree(root)
		# tree.write("IFTI-DRA2024080745.xml", encoding="utf-8", xml_declaration=True)
		xml_content = ET.tostring(root, encoding='utf-8', method='xml').decode('utf-8')
		return xml_content
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(str(e)+" in line "+str(exc_tb.tb_lineno))
		return bad_response(str(e)+" in line "+str(exc_tb.tb_lineno))


def create_austrac_ttr_xml_file(array, filename):
	try:
		# Create the root element
		ttr_msbList = ET.Element("ttr-msbList", xmlns="http://austrac.gov.au/schema/reporting/TTR-MSB-2-0")

		# Add the <reNumber> element
		reNumber = ET.SubElement(ttr_msbList, "reNumber")
		reNumber.text = XML_RE_NUMBER

		# Add the <fileName> element
		fileName = ET.SubElement(ttr_msbList, "fileName")
		fileName.text =  filename

		# Add the <reportCount> element
		reportCount = ET.SubElement(ttr_msbList, "reportCount")
		reportCount.text = str(len(array))

		for idx, item in enumerate(array, start=1):
			# Add the <ttr-msb> element
			ttr_msb = ET.SubElement(ttr_msbList, "ttr-msb", id="rpt-01")

			# Add the <header> element
			header = ET.SubElement(ttr_msb, "header", id="hdr-01-01")

			# Add the <txnRefNo> element
			txnRefNo = ET.SubElement(header, "txnRefNo")
			txnRefNo.text = "FX20111005-0235"

			# Add the <reportingBranch> element
			reportingBranch = ET.SubElement(header, "reportingBranch", id="rbr-01-01")

			# Add the <branchId> element
			branchId = ET.SubElement(reportingBranch, "branchId")
			branchId.text = "992221"

			# Add the <name> element
			name = ET.SubElement(reportingBranch, "name")
			name.text = "Ultimo"

			# Add the <address> element
			address = ET.SubElement(reportingBranch, "address", id="adr-01-01")

			# Add elements inside <address>
			addr = ET.SubElement(address, "addr")
			addr.text = "40A Harris Street"
			suburb = ET.SubElement(address, "suburb")
			suburb.text = "Ultimo"
			state = ET.SubElement(address, "state")
			state.text = "NSW"
			postcode = ET.SubElement(address, "postcode")
			postcode.text = "2007"

			# Add the <customer> element
			customer = ET.SubElement(ttr_msb, "customer", id="cst-01-01")

			# Add elements inside <customer>
			fullName = ET.SubElement(customer, "fullName")
			fullName.text = "John Citizen"
			mainAddress = ET.SubElement(customer, "mainAddress", id="adr-01-02")

			# Add elements inside <mainAddress>
			addr = ET.SubElement(mainAddress, "addr")
			addr.text = "U205C/601 High Street"
			suburb = ET.SubElement(mainAddress, "suburb")
			suburb.text = "Penrith"
			state = ET.SubElement(mainAddress, "state")
			state.text = "NSW"
			postcode = ET.SubElement(mainAddress, "postcode")
			postcode.text = "2751"
			country = ET.SubElement(mainAddress, "country")
			country.text = "Australia"

			# Add the <indOcc> element
			indOcc = ET.SubElement(customer, "indOcc", id="ioc-01-01")
			description = ET.SubElement(indOcc, "description")
			description.text = "Customer Service Manager"

			# Add the <dob> element
			dob = ET.SubElement(customer, "dob")
			dob.text = "1972-02-12"

			# Add the <identification> element
			identification = ET.SubElement(customer, "identification", id="idt-01-01")
			type = ET.SubElement(identification, "type")
			type.text = "D"
			number = ET.SubElement(identification, "number")
			number.text = "9999XX"
			issuer = ET.SubElement(identification, "issuer")
			issuer.text = "RTA NSW"
			country = ET.SubElement(identification, "country")
			country.text = "Australia"

			# Add the <electDataSrc> element
			electDataSrc = ET.SubElement(customer, "electDataSrc")
			electDataSrc.text = "World-Check"

			# Add the <individualConductingTxn> element
			individualConductingTxn = ET.SubElement(ttr_msb, "individualConductingTxn", id="ind-01-01")
			fullName = ET.SubElement(individualConductingTxn, "fullName")
			fullName.text = "Mary Citizen"
			mainAddress = ET.SubElement(individualConductingTxn, "mainAddress", id="adr-01-03")

			# Add elements inside <mainAddress> (for individual conducting transaction)
			addr = ET.SubElement(mainAddress, "addr")
			addr.text = "U205C/601 High Street"
			suburb = ET.SubElement(mainAddress, "suburb")
			suburb.text = "Penrith"
			state = ET.SubElement(mainAddress, "state")
			state.text = "NSW"
			postcode = ET.SubElement(mainAddress, "postcode")
			postcode.text = "2751"
			country = ET.SubElement(mainAddress, "country")
			country.text = "Australia"

			# Add the <recipient> element
			recipient = ET.SubElement(ttr_msb, "recipient", id="rcp-01-01")
			sameAsCustomer = ET.SubElement(recipient, "sameAsCustomer", refId="cst-01-01")

			# Add the <transaction> element
			transaction = ET.SubElement(ttr_msb, "transaction", id="txn-01-01")

			# Add the <txnDate> element
			txnDate = ET.SubElement(transaction, "txnDate")
			txnDate.text = "2011-10-05"

			# Add the <totalAmount> element
			totalAmount = ET.SubElement(transaction, "totalAmount", id="tam-01-01")
			currency = ET.SubElement(totalAmount, "currency")
			currency.text = "AUD"
			amount = ET.SubElement(totalAmount, "amount")
			amount.text = "36926.40"

			# Add the <designatedSvc> element
			designatedSvc = ET.SubElement(transaction, "designatedSvc")
			designatedSvc.text = "CUR_EXCH"

			# Add the <moneyReceived> element
			moneyReceived = ET.SubElement(transaction, "moneyReceived", id="mrv-01-01")
			cash = ET.SubElement(moneyReceived, "cash")
			foreignCash = ET.SubElement(cash, "foreignCash", id="fca-01-01")
			currency = ET.SubElement(foreignCash, "currency")
			currency.text = "EUR"
			amount = ET.SubElement(foreignCash, "amount")
			amount.text = "20000.00"

			# Add the <moneyProvided> element
			moneyProvided = ET.SubElement(transaction, "moneyProvided", id="mpr-01-01")
			cash = ET.SubElement(moneyProvided, "cash")
			ausCash = ET.SubElement(cash, "ausCash", id="csh-01-01")
			currency = ET.SubElement(ausCash, "currency")
			currency.text = "AUD"
			amount = ET.SubElement(ausCash, "amount")
			amount.text = "36900.00"

			# Add the <nonCashProvided> element
			nonCashProvided = ET.SubElement(moneyProvided, "nonCashProvided")
			fco = ET.SubElement(nonCashProvided, "fco")
			amount = ET.SubElement(fco, "amount")
			amount.text = "26.40"

		# Generate the tree and write to file
		tree = ET.ElementTree(ttr_msbList)
		xml_content = ET.tostring(ttr_msbList, encoding='utf-8', method='xml').decode('utf-8')
		return xml_content
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(str(e)+" in line "+str(exc_tb.tb_lineno))
		return bad_response(str(e)+" in line "+str(exc_tb.tb_lineno))
