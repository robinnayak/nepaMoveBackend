import string
import random
from rest_framework import serializers, status
from rest_framework.response import Response
from .models import Passenger
from authentication.serializers import CustomUserSerializer, OrganizationSerializer, DriverSerializer


class PassengerSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    class Meta:
        model = Passenger
        fields = '__all__'
        
        
        
        