from Remit_Assure.helpers import *
from Remit_Assure.package import *

transaction =  settings.TRANSACTION

""" New Customers """
def total_new_customers():
	new_customers = User.objects.filter(is_superuser=False).values('customer_id')
	new_customers_array = []
	for x in new_customers:
		if not Transaction_details.objects.filter(Q(payment_status=transaction['pending_review']) | Q(payment_status=transaction['completed']), customer_id=x['customer_id']).exists():
			new_customers_array.append(x['customer_id'])
	new_customers_count = len(new_customers_array)
	return new_customers_count

""" Total Payin Sum """
def total_payin_sum():
    payin = Transaction_details.objects.filter(Q(payment_status=transaction['pending_review']) | Q(payment_status=transaction['completed']), send_currency=settings.PAYIN_CURRENCY).aggregate(total=Sum('amount'))
    if payin['total']:
        return payin['total']
    else:
        return 0

""" Total Payout Sum """
def total_payout_sum():
    payout = Transaction_details.objects.filter(payment_status=transaction['completed'], send_currency=settings.PAYIN_CURRENCY).aggregate(total=Sum('amount'))
    if payout['total']:
        return payout['total']
    else:
        return 0

""" Payins, Payouts and Pending Payouts """
def payins_payouts(request):
    total_payin = total_payin_sum()
    total_payout = total_payout_sum()
    pending_payout = float(total_payin) - float(total_payout)
    return {
        'payin':PAYIN_CURRENCY+" "+comma_value(total_payin), 
        'payout': PAYIN_CURRENCY+" "+comma_value(total_payout), 
        'pending_payout':PAYIN_CURRENCY+" "+comma_value(pending_payout)
        }

""" Top 4 currencies data """
def top_4(sorted_data_AUD):
    i = 1
    dict = {}
    for d in sorted_data_AUD[:4]:
        #get amount total and number of transactions
        outflow = Transaction_details.objects.filter(send_currency="AUD", receive_currency=d['currency']).aggregate(total=Sum('amount'))
        count = Transaction_details.objects.filter(send_currency="AUD", receive_currency=d['currency']).count()
        outflow['total'] = comma_value(outflow['total'])
        dict["top"+str(i)+"_outflow"] = outflow['total']
        dict["top"+str(i)+"_count"] = count
        dict["top"+str(i)] = d['country']+" ("+d['currency']+")"
        i += 1  
    return dict

""" Remittance By Corridors """
def remittance_by_corridors(request):
    AUD_transactions = []
    dict = {}

    #payout currencies
    payout_currencies = RECEIVE_CURRENCY_LIST

    #get counts for currencies from transactions
    for c in payout_currencies:
        currency = str(c['currency']).upper()
        send_currency = "AUD"
        send_count = Transaction_details.objects.filter(send_currency=send_currency, receive_currency=currency).count()
        dict = {'currency':currency, 'country':c['country'], 'count':send_count}
        AUD_transactions.append(dict)

    #sorting list according to transaction counts    
    sorted_data_AUD = sorted(AUD_transactions, key=lambda x: x['count'], reverse=True)

    #top 4 payout currencies outflow, number of transactions, and currencies
    post_dict = top_4(sorted_data_AUD)
  
    #last five transactions
    transactions = Transaction_details.objects.all().order_by('-updated_at')[:5]
    for x in transactions:
        x.amount = comma_value(x.amount)
        x.exchange_rate = comma_value(x.exchange_rate)
        x.receive_amount = comma_value(x.receive_amount)
    post_dict.update(transactions = transactions)
    return post_dict


