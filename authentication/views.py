from django.shortcuts import render
from rest_framework.views import APIView    
# Create your views here.
from .models import CustomUser
from .serializers import CustomUserSerializer,CustomUserLoginSerializer
from .renderers import UserRenderer 
from django.contrib.auth import authenticate,login,logout

from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken  
 
from django.contrib.auth.models import Group 


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
                token = get_tokens_for_user(user)
                if user.is_organization:
                    group = Group.objects.get(name='organization')
                    user.groups.add(group)
                else:
                    group = Group.objects.get(name='passenger')
                    user.groups.add(group)
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