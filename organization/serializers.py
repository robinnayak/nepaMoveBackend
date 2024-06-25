import string
import random
from rest_framework import serializers, status
from rest_framework.response import Response
from .models import Vehicle, Organization, Driver, Trip, Booking, TripPrice, Ticket
from authentication.serializers import OrganizationSerializer, DriverSerializer
from passenger.serializers import PassengerSerializer
class VehicleSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    driver = DriverSerializer(read_only=True)
    
    class Meta:
        model = Vehicle
        fields = '__all__'

    def create(self, validated_data):
        org_email = self.context.get('org_email')
        dri_license = self.context.get('dri_license')
        check_driver = self.context.get('check_driver')

        validated_data = self._assign_organization_and_driver(validated_data, org_email, dri_license,check_driver)
        if isinstance(validated_data, Response):  # Error response from _assign_organization_and_driver
            return validated_data

        veh_id = self._generate_random_string()
        reg_id = self._generate_registration_number(veh_id, validated_data['organization'].user.username)
        validated_data['registration_number'] = reg_id

        vehicle = Vehicle.objects.create(**validated_data)
        return vehicle

    def _assign_organization_and_driver(self, validated_data, org_email, dri_license,check_driver):
        try:
            if check_driver:
                # user_dri_check = Vehicle.objects.filter(driver__license_number=dri_license).exists()
                # if user_dri_check:
                #     return Response({"message": "Driver already has a vehicle"}, status=status.HTTP_400_BAD_REQUEST)
                driver_license = Driver.objects.get(license_number=dri_license)
                validated_data['driver'] = driver_license
            else:
                return serializers.ValidationError({"message":"Driver not exist related with this organization "}, status=status.HTTP_400_BAD_REQUEST)
            if org_email:
                
                # user_org_check = Driver.objects.filter(organization__user_email=org_email).exists()
                # if user_org_check:
                #     return Response({"message": "Organization already has a vehicle"}, status=status.HTTP_400_BAD_REQUEST)
                org_mail = Organization.objects.get(user__email=org_email)
                validated_data['organization'] = org_mail

        except Organization.DoesNotExist:
            return Response({"message": "Organization not found"}, status=status.HTTP_404_NOT_FOUND)
        except Driver.DoesNotExist:
            return Response({"message": "Driver not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        return validated_data

    @staticmethod
    def _generate_random_string(length=10):
        characters = string.ascii_letters + string.digits
        result = ''.join(random.choice(characters) for _ in range(length))
        return result

    @staticmethod
    def _generate_registration_number(id, username):
        prefix = f"{id}{username}"
        return prefix.upper()


class TripSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    class Meta:
        model = Trip
        fields = '__all__'
        
    def create(self, validated_data):
        org_email = self.context.get('org_email')
        print("org_email",org_email)
        try:
            org_mail = Organization.objects.get(user__email=org_email)
            validated_data['organization'] = org_mail
        except Organization.DoesNotExist:
            return Response({"message": "Organization not found"}, status=status.HTTP_404_NOT_FOUND)
        trip = Trip.objects.create(**validated_data)
        return trip
    
class TripPriceSerializer(serializers.ModelSerializer):
    trip = TripSerializer(read_only=True)
    vehicle = VehicleSerializer(read_only=True)
    class Meta:
        model = TripPrice
        fields = '__all__'
        
        
class BookingSerializer(serializers.ModelSerializer):
    passennger = PassengerSerializer(read_only=True)
    trip_price = TripPriceSerializer(read_only=True)
    class Meta:
        model = Booking
        fields = '__all__'
        
    
class TicketSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)
    class Meta:
        model = Ticket
        fields = '__all__'
        
    

    
    
    