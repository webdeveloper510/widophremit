from django.shortcuts import render
from Remit_Assure import settings
from Remit_Assure.package import *
import uuid


class DirectCreditView(APIView):
    def post(self, request):
        return False
    
class DirectDebitView(APIView):
    permission_classes=[IsAuthenticated] 
    def post(self, request):
        try:
            # user_data = User.objects.filter(id=2).values()
            # user_data_list = list(user_data)
            user_id = request.user.id
            user_data_list = get_object_or_404(User,id=user_id)
            payment_mode = data.get("payment_mode")
            data = json.loads(request.body)
            # Recipient | # Recipient_bank_details
            # recipient_id = 2
            # recipient_bank_details = get_object_or_404(Recipient_bank_details,recipient_id=recipient_id)
            if payment_mode == 'debit':
                payload = {
                    "totalAmount": data.get("amount"),
                    "paymentSource": "directDebit",
                    # "lodgementReference": data.get("lodgementReference", "monoova-123"),
                    "description": data.get("description") or "",
                    "directDebit": {
                        "bsbNumber": data.get("bsbNumber"),
                        "accountNumber": data.get("accountNumber"),
                        "accountName": data.get("accountName")
                        # "bsbNumber": recipient_bank_details.swift_code,
                        # "accountNumber": recipient_bank_details.account_number,
                        # "accountName": recipient_bank_details.account_name
                    }
                }
            elif payment_mode == 'npp':
                payload = {
                    "totalAmount": data.get("amount"),
                    "disbursements": [
                        {
                        "disbursementMethod": "NppCreditBankAccount",
                        "toNppCreditBankAccountDetails": {
                            "bsbNumber": data.get("bsbNumber"),
                            "accountNumber": data.get("accountNumber"),
                            "accountName": data.get("accountName"),
                            "endToEndId": "INV/001-5678",
                            "remitterName": "Widoph Remit"
                        },
                        # "lodgementReference": "string",
                        "amount": data.get("amount")
                        }
                    ],
                    "description": data.get("description") or ""
                    }
            url = "https://api.m-pay.com.au/financial/v2/transaction/execute"
            headers = {
                "Authorization": "83224362-77E8-4CE3-BA96-6A59D1BD83DB",
                "Content-Type": "application/json",
            }
            response = requests.post(url, json=payload, headers=headers)
            response_data = response.json()
            # print('response_data',response_data)
            dataRes = {
                "customer_id": user_data_list.customer_id,
                "recipient_name": f"{user_data_list.First_name} {user_data_list.Last_name}",
                "send_currency": 'AUD',
                "receive_currency": 'NGN',
                "amount": data.get("amount"),
                "total_amount": data.get("amount"),
                "receive_amount": data.get("amount"),
                "send_method": "Monoova_payin_per_user",
                "receive_method": "Bank transfer",
                "payout_partner": "",
                "exchange_rate": 1000.00,
                "payment_status": TRANSACTION.pending_review if response_data.get("transactionId") else TRANSACTION.incomplete,
                "payment_status_reason": response_data.get("statusDescription") or "",
                "transaction_id": response_data.get("transactionId"),
                "reason": response_data.get("reason") or "",
                "date": datetime.strptime(datetime.today().strftime("%Y-%m-%d"), "%Y-%m-%d").date(),
            }
            # print('dataRes',dataRes)

            # Transaction_details.objects.create(**dataRes)
            # print('transactionId',response_data.get('transactionId'))
            return JsonResponse(response_data, status=response.status_code)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    