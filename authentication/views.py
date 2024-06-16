from django.shortcuts import render
from rest_framework.views import APIView    
# Create your views here.
from .models import CustomUser
from .serializers import CustomUserSerializer,CustomUserLoginSerializer,OrganizationSerializer,DriverSerializer
from .renderers import UserRenderer 
from django.contrib.auth import authenticate,login,logout

from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken  
 
from django.contrib.auth.models import Group 
from . import models


def get_tokens_for_user(user):
    refersh = RefreshToken.for_user(user)
    return{
        'refresh':str(refersh),
        'access':str(refersh.access_token)
    }
    


class RegistrationView(APIView):
    renderer_classes = [UserRenderer]
    def get(self,request):
        users = CustomUser.objects.all()   
        try: 
            serializer = CustomUserSerializer(users,many=True)  
            return Response((serializer.data),status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST) 
        
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        try:
            if serializer.is_valid():
                user = serializer.save()
                if user.is_organization:
                    print("organizaton...")
                    group = Group.objects.get(name='organization')
                    user.groups.add(group)
                    organization = models.Organization.objects.create(user=user)
                    print("organization 1: ",organization)
                    if organization is not None:
                        token = get_tokens_for_user(user)
                    
                    print("organization",organization)
                elif user.is_driver:
                    print("driver...")
                    group = Group.objects.get(name='driver')
                    user.groups.add(group)
                    driver = models.Driver.objects.create(user=user)
                    print("driver 1: ",driver)
                    if driver is not None:
                        token = get_tokens_for_user(user)
                    print("driver",driver)
                else:
                    group = Group.objects.get(name='passenger')
                    user.groups.add(group)
                    token = get_tokens_for_user(user)
                message = {
                    'message': 'User created successfully',
                    'user': serializer.data,
                    'token': token
                }
                return Response(message, status=status.HTTP_201_CREATED)
            else:
                if 'non_field_errors' in serializer.errors:
                    return Response(serializer.errors['non_field_errors'], status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
class LoginView(APIView):
    def post(self, request):
        try:
            serializer = CustomUserLoginSerializer(data=request.data)
            if serializer.is_valid():
                username = serializer.validated_data['username']
                password = serializer.validated_data['password']
                user = authenticate(username=username, password=password)
                user = CustomUser.objects.get(username=username)
                if user:
                    login(request, user)
                    token = get_tokens_for_user(user)   
                    
                    message = {
                        'message': 'User logged in successfully',
                        'user': CustomUserSerializer(user).data,
                        'token': token
                    }
                    return Response(message, status=status.HTTP_200_OK)
           
            else:
                if 'non_field_errors' in serializer.errors:
                    return Response(serializer.errors['non_field_errors'], status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
class LogoutView(APIView):
    def get(self,request):
        try:
            user = logout(request)
            print("user",user)  
            message = {
                'message': 'User logged out successfully',
                'user':user    

            }
            return Response(message, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        

class OrganizationView(APIView):
    renderer_classes = [UserRenderer]
    def get(self,request):
        organizations = models.Organization.objects.all()
        try:
            serializer = OrganizationSerializer(organizations,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)
    
    def post(self,request):
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            group = Group.objects.get(name='organization')
            user.groups.add(group)
            organization = models.Organization.objects.create(user=user)
            message = {
                'message': 'Organization created successfully',
                'user': serializer.data
            }
            return Response(message, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class OrganizationDetailView(APIView):
    renderer_classes = [UserRenderer]
    def get(self,request,pk):
        organization = models.Organization.objects.get(id=pk)
        serializer = OrganizationSerializer(organization)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def put(self,request,pk):
        
        
        organization = models.Organization.objects.get(id=pk)
        phone_number = request.data.get('phone_number')
        print("phone_number inside view: ",phone_number)
        serializer = OrganizationSerializer(organization,data=request.data,context={"phone_number":phone_number})
        if serializer.is_valid():
            serializer.save()
            message = {
                'message': 'Organization updated successfully',
                'user': serializer.data
            }
            return Response(message, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,pk):
        organization = models.Organization.objects.get(id=pk)
        organization.delete()
        message = {
            'message': 'Organization deleted successfully'
        }
        return Response(message, status=status.HTTP_200_OK)
    
class DriverDetailView(APIView):
    renderer_classes = [UserRenderer]
    def get(self,request,pk):
        driver = models.Driver.objects.get(id=pk)
        serializer = DriverSerializer(driver)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def put(self,request,pk):
        driver = models.Driver.objects.get(id=pk)
        phone_number = request.data.get('phone_number')
        print("phone_number inside view: ",phone_number)
        serializer = DriverSerializer(driver,data=request.data,context={"phone_number":phone_number})
        if serializer.is_valid():
            serializer.save()
            message = {
                'message': 'Driver updated successfully',
                'user': serializer.data
            }
            return Response(message, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,pk):
        driver = models.Driver.objects.get(id=pk)
        driver.delete()
        message = {
            'message': 'Driver deleted successfully'
        }
        return Response(message, status=status.HTTP_200_OK) 