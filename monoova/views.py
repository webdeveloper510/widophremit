from django.shortcuts import render
from Widoph_Remit import settings
from Widoph_Remit.package import *
import uuid


class DirectCreditView(APIView):
    def post(self, request):
        return False
    
class DirectDebitView(APIView):
    permission_classes=[IsAuthenticated] 
    def post(self, request):
        try:
            user_id = request.user.id
            user_data = User.objects.filter(id=user_id).values()
            user_data_list = list(user_data)
            data = json.loads(request.body)

            payment_mode = data.get("payment_mode")
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
                        # "lodgementReference": data.get("lodgementReference", "monoova-123"),
                        "amount": data.get("amount")
                        }
                    ],
                    "description": data.get("description") or ""
                    }
            url = f"{settings.MONOOVA_API_ENDPOINT}/financial/v2/transaction/execute"
            headers = {
                "Authorization": "83224362-77E8-4CE3-BA96-6A59D1BD83DB",
                "Content-Type": "application/json",
            }
            response = requests.post(url, json=payload, headers=headers)
            response_data = response.json()
            dataRes = {
                "customer_id": user_data_list[0].get("customer_id"),
                "recipient_name": f'{user_data_list[0].get("First_name")} {user_data_list[0].get("Last_name")}',
                "send_currency": 'AUD',
                "receive_currency": 'NGN',
                "amount": data.get("amount"),
                "total_amount": data.get("amount"),
                "receive_amount": data.get("amount"),
                "send_method": "Monoova_payin_per_user",
                "receive_method": "Bank transfer",
                "payout_partner": "",
                "exchange_rate": 1000.00,
                "payment_status": TRANSACTION.get('pending_review') if response_data.get("transactionId") else TRANSACTION.get('incomplete'),
                "payment_status_reason": response_data.get("statusDescription") or "",
                "transaction_id": response_data.get("transactionId"),
                "reason": response_data.get("reason") or "",
                "date": datetime.strptime(datetime.today().strftime("%Y-%m-%d"), "%Y-%m-%d").date(),
            }
            Transaction_details.objects.create(**dataRes)
            return JsonResponse(response_data, status=response.status_code)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    