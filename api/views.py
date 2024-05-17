from django.shortcuts import render, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
# Create your views here.

def index(request):
    
    return HttpResponse("Hello, world. You're at the polls index.")


# class Home(APIView):
#     def get(self, request, *args, **kwargs):
#         message = "Hello, world. You're at the polls index."
#         data = json.dumps(message)
#         return Response(data,status=status.HTTP_200_OK)