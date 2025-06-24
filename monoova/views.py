from django.shortcuts import render
from Remit_Assure import settings
from Remit_Assure.package import *



class DirectCreditView(APIView):
    def post(self, request):
        return False
    
class DirectDebitView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            payload = {
                "totalAmount": data.get("amount"),
                "paymentSource": "directDebit",
                # "lodgementReference": data.get("lodgementReference", "monoova-123"),
                "description": data.get("description"),
                "directDebit": {
                    "bsbNumber": data.get("bsbNumber"),
                    "accountNumber": data.get("accountNumber"),
                    "accountName": data.get("accountName")
                }
            }
            url = "https://api.m-pay.com.au/financial/v2/transaction/execute"
            headers = {
                "Authorization": "83224362-77E8-4CE3-BA96-6A59D1BD83DB",
                "Content-Type": "application/json",
            }
            response = requests.post(url, json=payload, headers=headers)
            response_data = response.json()
            # print('transactionId',response_data.get('transactionId'))
            return JsonResponse(response_data, status=response.status_code)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    