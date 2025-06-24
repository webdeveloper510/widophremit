


    











           # created_time = User.objects.filter(email_otp = email_otp_code).values('created_at')
        # created_time = str(created_time[0]['created_at'])
        # created_time = created_time[:19]
        # created_time = datetime.strptime(created_time, '%Y-%m-%d %H:%M:%S')
        # created_time = created_time.time()
        # expire_time = created_time + settings.TOKEN_EXPIRED_AFTER_SECONDS
        # print(created_time, expire_time)
         
        # created = User.objects.filter(email)
        # expire_time = verification_token.created + settings.TOKEN_EXPIRED_AFTER_SECONDS
        # is_token_expired =  expire_time < timezone.now()
        # if is_token_expired == True:
        #         verification_token.delete()
        #         User.objects.filter(id=id).update(is_verified=False)
        #         return render(request, "token_expired.html")
        #     else:
        #         User.objects.filter(id=id).update(is_verified=True)
        # else:
        #     return render(request, "token_expired.html")
        
        # return render(request, "email_verified.html")



# class SendResetPasswordEmailView(APIView):
#     renderer_classes=[UserRenderer]
#     def post(self, request, format=None):
#         email = request.data.get('email')
#         if not email:
#             raise serializers.ValidationError({"status":"status.HTTP_400_BAD_REQUEST","message":"Please enter your email"})
#         if email and not '@' in email:
#             raise serializers.ValidationError({"status":"status.HTTP_400_BAD_REQUEST","message":"Please enter a valid email address"})
#         if email and not '.' in email:
#             raise serializers.ValidationError({"status":"status.HTTP_400_BAD_REQUEST","message":"Please enter a valid email address"})
#         if email and not User.objects.filter(email=email).exists():
#             raise serializers.ValidationError({"status":"status.HTTP_400_BAD_REQUEST","message":"You are not a registered user"})
#         user = User.objects.filter(email = email).values('id')
#         uid = urlsafe_base64_encode(force_bytes(user[0]['id']))
#         reset_password_code = Reset_Password_token.objects.filter(uid=uid).values('key')
#         serializer = SendPasswordResetEmailSerializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             return Response({'token':reset_password_code,'msg':'Reset Password OTP has been sent on your email Please check your Email','status':'status.HTTP_200_OK'})
#         return Response({errors:serializer.errors},status=status.HTTP_400_BAD_REQUEST)

# class ResetPasswordView(APIView):
#     renderer_classes = [UserRenderer]
#     def post(self, request, token, format=None):
#         password =request.data.get('password')
#         if not password:
#             raise serializers.ValidationError({"status":"status.HTTP_400_BAD_REQUEST","message":"Please enter new password"})
#         serializer = UserPasswordResetSerializer(data=request.data, context={'token':token})
#         if serializer.is_valid(raise_exception=True):
#             print("serializer data",serializer.data)
#             return Response({'msg':'Password Reset Successfully', 'status':'status.HTTP_200_OK'})
#         return Response({errors:serializer.errors},status=status.HTTP_400_BAD_REQUEST)