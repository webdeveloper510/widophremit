from rest_framework.response import Response
from rest_framework import status

def success_response(message, data=None):
    if not data:
        return Response({'code': "200", 'message':message})
    else:
        return Response({'code': "200", 'message':message, 'data':data})

def token_response(message, token, data=None):
    if data == None:
        return Response({"code": "200","message": str(message),"access_token":token}) 
    else:
        return Response({"code": "200","message": str(message),"access_token":token,"data": data}) 

def bad_response(message):
    response = Response({"code": "400", "message": str(message)})
    return response

def pending_verification_response(message, data):
    if data:
        response = Response({
        "code": "201",
        "message": str(message),
        "data": data
    }) 
    else:
        response = Response({
        "code": "201",
        "message": str(message),
    }) 
    return response



# debug toolbar response
from django.shortcuts import render
def view_response(request,context):
    return render(request,'mophy/testing_debug.html',context)
