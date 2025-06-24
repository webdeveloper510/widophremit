# import requests

# #==================check balance ===========

# url1 = "https://devapi.currencycloud.com/v2/balances/find"
# payload={}
# headers = {
#   'X-Auth-Token': 'b814778f215d36b29645866974a975b8',
#   'Accept': 'application/json'
# }
# response1 = requests.request("GET", url1, headers=headers, data=payload)
# response1 = response1.json()


# # =========== Get detaild rates and check cutoff time =========== 
# url2 = "https://devapi.currencycloud.com/v2/rates/detailed?buy_currency=USD&sell_currency=AUD&fixed_side=sell&amount=500"
# payload={}
# headers = {
#   'X-Auth-Token': 'b814778f215d36b29645866974a975b8',
#   'Accept': 'application/json'
# }
# response2 = requests.request("GET", url2, headers=headers, data=payload)
# response2 = response2.json()


# # ============= Create conversions ====================
# url3 = "https://devapi.currencycloud.com/v2/conversions/create"
# payload={'buy_currency': 'USD',
# 'sell_currency': 'AUD',
# 'fixed_side': 'sell',
# 'amount': '500',
# 'term_agreement': 'true',
# 'reason': 'testing'}

# headers = {
#   'X-Auth-Token': 'b814778f215d36b29645866974a975b8',
#   'Content-Type': 'multipart/form-data',
#   'Accept': 'application/json'
# }
# response3 = requests.request("POST", url3, headers=headers, data=payload)
# response3 = response3.json()


# #  ============= Create payment ============

# url = "https://devapi.currencycloud.com/v2/payments/create"

# payload={'currency': 'EUR',
# 'beneficiary_id': '0fa6094d-2835-493d-af9a-235b86c57f64',
# 'amount': '300',
# 'reason': 'Invoice Payment',
# 'reference': '2023 Test',
# 'payment_type': 'regular',
# 'conversion_id': '90005808-4e83-4ace-9fa1-167a91d4451b',
# 'unique_request_id': '444'}
# files=[

# ]
# headers = {
#   'X-Auth-Token': 'b814778f215d36b29645866974a975b8',
#   'Content-Type': 'multipart/form-data',
#   'Accept': 'application/json'
# }

# response = requests.request("POST", url, headers=headers, data=payload, files=files)



import socket   
hostname=socket.gethostname()   
IPAddr=socket.gethostbyname(hostname)   
print("Your Computer Name is:"+hostname)   
print("Your Computer IP Address is:"+IPAddr)   