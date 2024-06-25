from django.shortcuts import render
from . import serializers
from rest_framework.views import APIView
from authentication.renderers import UserRenderer
# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Vehicle,Trip,Booking,TripPrice,Ticket
from authentication.models import Driver,Organization
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import stripe



class VehicleView(APIView):
    permission_classes = [IsAuthenticated]
    
    renderer_classes = [UserRenderer]
    def get(self,request):
        vehicles = Vehicle.objects.all()
        try:
            serializer = serializers.VehicleSerializer(vehicles,many=True)

            return Response(serializer.data,status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST) 
        
    def post(self,request,*args,**kwargs):
        
        if request.user.is_organization:
            dri_license = request.data['license_number']
            check_driver = Driver.objects.filter(organization__user__email=request.user.email,license_number=dri_license).exists()
            print("check driver",check_driver)
            # check_org = Vehicle.objects.filter(organization__user__email=request.user.email,driver__organization__user__email=request.user.email).exists()
            context = {
                # 'check_org':check_org,
                'org_email':request.user.email,
                'dri_license':dri_license,
                'check_driver': check_driver
            }
            
            # if check_org:
            #     return Response({"message":f"This Organization {request.user.email} already has a vehicle with this driver"},status=status.HTTP_400_BAD_REQUEST)
            
            serializer = serializers.VehicleSerializer(data=request.data,context=context)
            try:
                if serializer.is_valid():
                    serializer.save()
                    message = {
                        "message":"Vehicle data retrieved successfully",
                        "data":serializer.data
                    }
                    return Response(message,status.HTTP_201_CREATED)
                else:
                    if 'non_field_errors' in serializer.errors:
                        return Response(serializer.errors['non_field_errors'],status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response(str(e),status=status.HTTP_400_BAD_REQUEST)
    
        
class VehicleDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request,reg_id):
        try:
            vehicle = Vehicle.objects.get(registration_number=reg_id)
            serializer = serializers.VehicleSerializer(vehicle)
            return Response(serializer.data,status.HTTP_200_OK)
        except Vehicle.DoesNotExist:
            return Response({"message":"Vehicle not found"},status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)
        
    def put(self,request,reg_id):
        try:
            if request.user.is_organization:
                check_org = Vehicle.objects.filter(organization__user__email=request.user.email).exists()
                if check_org:
                    vehicle = Vehicle.objects.get(registration_number=reg_id,organization__user__email=request.user.email)
                    serializer = serializers.VehicleSerializer(vehicle,data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        message = {
                            "message":"Vehicle data updated successfully",
                            "data":serializer.data
                        }
                        return Response(message,status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"message":"Organization does not have a vehicle"},status.HTTP_400_BAD_REQUEST)
            elif request.user.is_driver:    
                check_driver = Vehicle.objects.filter(driver__user__email=request.user.email).exists()
                if check_driver:
                    vehicle = Vehicle.objects.get(registration_number=reg_id,driver__user__email=request.user.email)
                    serializer = serializers.VehicleSerializer(vehicle,data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        message = {
                            "message":"Vehicle data updated successfully",
                            "data":serializer.data
                        }
                        return Response(message,status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)          
            else:
                return Response({"message":"User is not an registered driver or organization relted"},status.HTTP_400_BAD_REQUEST)
        except Vehicle.DoesNotExist:
            return Response({"message":"Vehicle not found"},status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)
        
    def delete(self,request,reg_id):
        try:
            if request.user.is_driver:
                check_driver = Vehicle.objects.filter(driver__user__email=request.user.email).exists()
                if check_driver:
                    vehicle = Vehicle.objects.get(registration_number=reg_id,driver__user__email=request.user.email)
                    vehicle.delete()
                else:
                    return Response({"message":"Driver does not have a vehicle"},status.HTTP_400_BAD_REQUEST)
            elif request.user.is_organization:
                check_org = Vehicle.objects.filter(organization__user__email=request.user.email).exists()
                if check_org:
                    vehicle = Vehicle.objects.get(registration_number=reg_id,organization__user__email=request.data['email'])
                    vehicle.delete()
                return Response({"message":"Vehicle deleted successfully"},status.HTTP_200_OK)
        except Vehicle.DoesNotExist:
            return Response({"message":"Vehicle not found"},status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)
        
        
class TripView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        trips = Trip.objects.all()
        try:
            serializer = serializers.TripSerializer(trips,many=True)
            return Response(serializer.data,status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)
        
    def post(self,request):
        if request.user.is_organization:    
            serializer = serializers.TripSerializer(data=request.data,context={'org_email':request.user.email})
            try:
                if serializer.is_valid():
                    serializer.save()
                    message = {
                        "message":"Trip data retrieved successfully",
                        "data":serializer.data
                    }
                    return Response(message,status.HTTP_201_CREATED)
                else:
                    if 'non_field_errors' in serializer.errors:
                        return Response(serializer.errors['non_field_errors'],status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response(str(e),status.HTTP_400_BAD_REQUEST)     
        else:
            return Response({"message":"User is not an organization"},status.HTTP_400_BAD_REQUEST)
class TripDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,trip_id):
        try:
            trip = Trip.objects.get(trip_id=trip_id,organization__user__username=request.user.username)
            serializer = serializers.TripSerializer(trip)
            return Response(serializer.data,status.HTTP_200_OK)
        except Trip.DoesNotExist:
            return Response({"message":"Trip not found"},status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)
        
    def put(self,request,trip_id):
        try:
            trip = Trip.objects.get(trip_id=trip_id,organization__user__username=request.user.username)
            serializer = serializers.TripSerializer(trip,data=request.data)
            if serializer.is_valid():
                serializer.save()
                message = {
                    "message":"Trip data updated successfully",
                    "data":serializer.data
                }
                return Response(message,status.HTTP_200_OK)
            else:
                return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)
        except Trip.DoesNotExist:
            return Response({"message":"Trip not found"},status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)
        
    def delete(self,request,trip_id):
        try:
            trip = Trip.objects.get(trip_id=trip_id,organization__user__username=request.user.username)
            trip.delete()
            return Response({"message":"Trip deleted successfully"},status.HTTP_200_OK)
        except Trip.DoesNotExist:
            return Response({"message":"Trip not found"},status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)

            
class TripPriceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        trip_prices = TripPrice.objects.all()
        try:
            serializer = serializers.TripPriceSerializer(trip_prices,many=True)
            return Response(serializer.data,status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)
        
    def post(self,request):
        serializer = serializers.TripPriceSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                message = {
                    "message":"Trip Price data retrieved successfully",
                    "data":serializer.data
                }
                return Response(message,status.HTTP_201_CREATED)
            else:
                if 'non_field_errors' in serializer.errors:
                    return Response(serializer.errors['non_field_errors'],status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)
        
class TripPriceDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request,trip_price_id):
        try:
            trip_price = TripPrice.objects.get(trip_price_id=trip_price_id, trip__organization__user__username=request.user.username, vehicle__organization__user__username=request.user.username)
            serializer = serializers.TripPriceSerializer(trip_price)
            return Response(serializer.data,status.HTTP_200_OK)
        except TripPrice.DoesNotExist:
            return Response({"message":"Trip Price not found"},status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)
        
    def put(self,request,trip_price_id):
        try:
            trip_price = TripPrice.objects.get(trip_price_id=trip_price_id, trip__organization__user__username=request.user.username, trip__vehicle__organization__user__username=request.user.username)
            
            serializer = serializers.TripPriceSerializer(trip_price,data=request.data)
            if serializer.is_valid():
                serializer.save()
                message = {
                    "message":"Trip Price data updated successfully",
                    "data":serializer.data
                }
                return Response(message,status.HTTP_200_OK)
            else:
                return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)
        except TripPrice.DoesNotExist:
            return Response({"message":"Trip Price not found"},status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)
        
    def delete(self,request,trip_price_id):
        try:
            trip_price = TripPrice.objects.get(trip_price_id=trip_price_id, trip__organization__user__username=request.user.username, trip__vehicle__organization__user__username=request.user.username)
            trip_price.delete()
            return Response({"message":"Trip Price deleted successfully"},status.HTTP_200_OK)
        except TripPrice.DoesNotExist:
            return Response({"message":"Trip Price not found"},status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)
        
class BookingView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        bookings = Booking.objects.all()
        try:
            serializer = serializers.BookingSerializer(bookings,many=True)
            return Response(serializer.data,status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)
        
    def post(self,request):
        serializer = serializers.BookingSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                message = {
                    "message":"Booking data retrieved successfully",
                    "data":serializer.data
                }
                return Response(message,status.HTTP_201_CREATED)
            else:
                if 'non_field_errors' in serializer.errors:
                    return Response(serializer.errors['non_field_errors'],status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)
        
class BookingDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request,booking_id):
        try:
            if request.user.is_driver:
                booking = Booking.objects.get(booking_id=booking_id,tripprice__vehicle__driver__user__username=request.user.username)
            elif request.user.is_organization:
                booking = Booking.objects.get(booking_id=booking_id,tripprice__trip__organization__user__username=request.user.username)
            else:
                booking = Booking.objects.get(booking_id=booking_id,passenger__user__username=request.user.username)
            
            serializer = serializers.BookingSerializer(booking)
            return Response(serializer.data,status.HTTP_200_OK)
        except Booking.DoesNotExist:
            return Response({"message":"Booking not found"},status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)
        
    def put(self,request,booking_id):
        try:
            booking = Booking.objects.get(booking_id=booking_id)
            serializer = serializers.BookingSerializer(booking,data=request.data)
            if serializer.is_valid():
                serializer.save()
                message = {
                    "message":"Booking data updated successfully",
                    "data":serializer.data
                }
                return Response(message,status.HTTP_200_OK)
            else:
                return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)
        except Booking.DoesNotExist:
            return Response({"message":"Booking not found"},status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)
        
    def delete(self,request,booking_id):
        try:
            booking = Booking.objects.get(booking_id=booking_id)
            booking.delete()
            return Response({"message":"Booking deleted successfully"},status.HTTP_200_OK)
        except Booking.DoesNotExist:
            return Response({"message":"Booking not found"},status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)
        
class TicketView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        tickets = Ticket.objects.all()
        try:
                            
            serializer = serializers.TicketSerializer(tickets,many=True)
            return Response(serializer.data,status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)
        
    def post(self,request):
        serializer = serializers.TicketSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                message = {
                    "message":"Ticket data retrieved successfully",
                    "data":serializer.data
                }
                return Response(message,status.HTTP_201_CREATED)
            else:
                if 'non_field_errors' in serializer.errors:
                    return Response(serializer.errors['non_field_errors'],status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)

class TicketDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request,ticket_id):
        
        try:
            if request.user.is_driver:
                ticket = Ticket.objects.filter(booking__tripprice__vehicle__driver__user__username=request.user.username)
            elif request.user.is_organization:
                ticket = Ticket.objects.filter(booking__tripprice__trip__organization__user__username=request.user.username)
            else:
                ticket = Ticket.objects.filter(booking__passenger__user__username=request.user.username)
            serializer = serializers.TicketSerializer(ticket,many=True)
            return Response(serializer.data,status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            return Response({"message":"Ticket not found"},status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)
        
    def put(self,request,ticket_id):
        try:
            if request.user.is_driver:
                ticket = Ticket.objects.filter(booking__tripprice__vehicle__driver__user__username=request.user.username)
            elif request.user.is_organization:
                ticket = Ticket.objects.filter(booking__tripprice__trip__organization__user__username=request.user.username)
            else:
                ticket = Ticket.objects.filter(booking__passenger__user__username=request.user.username)
            serializer = serializers.TicketSerializer(ticket,data=request.data,many=True)
            if serializer.is_valid():
                serializer.save()
                message = {
                    "message":"Ticket data updated successfully",
                    "data":serializer.data
                }
                return Response(message,status.HTTP_200_OK)
            else:
                return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)
        except Ticket.DoesNotExist:
            return Response({"message":"Ticket not found"},status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)
        
    def delete(self,request,ticket_id):
        try:
            if request.user.is_driver:
                ticket = Ticket.objects.filter(booking__tripprice__vehicle__driver__user__username=request.user.username)
            elif request.user.is_organization:
                ticket = Ticket.objects.filter(booking__tripprice__trip__organization__user__username=request.user.username)
            else:
                ticket = Ticket.objects.filter(booking__passenger__user__username=request.user.username)
            ticket.delete()
            return Response({"message":"Ticket deleted successfully"},status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            return Response({"message":"Ticket not found"},status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)




