from django.db import models
from rest_framework import serializers, status
from rest_framework.response import Response
from django.utils import timezone
from django.conf import settings
from authentication.models import Driver, Organization
from passenger.models import Passenger
import os
import random
import string


class Vehicle(models.Model):
    REGISTRATION_CHOICES = (
        ('car', 'Car'),
        ('van', 'Van'),
        ('motorcycle', 'Motorcycle'),
        # Add more vehicle types as needed
    )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True, related_query_name="vehicle_organization")
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, blank=True, related_query_name="vehicle_driver")
    registration_number = models.CharField(default="WXY123ABC", max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=10, choices=REGISTRATION_CHOICES)
    company_made = models.CharField(max_length=50, blank=True)
    model = models.CharField(max_length=50, blank=True)
    age = models.IntegerField(default=18)
    color = models.CharField(max_length=30, default="black")
    seating_capacity = models.PositiveIntegerField(default=0)
    license_plate_number = models.CharField(max_length=10, unique=True)
    insurance_expiry_date = models.DateField(auto_now_add=True)
    fitness_certificate_expiry_date = models.DateField(auto_now_add=True)
    image = models.ImageField(upload_to='vehicle_images', blank=True)
    available_seat = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.available_seat == 0:
            self.available_seat = self.seating_capacity
            print("=====================================")
            print("seating capacity",self.seating_capacity)
            print("available seat",self.available_seat)
            print("=====================================")
            
        elif self.available_seat <= 0:
            raise serializers.ValidationError("Available seats cannot be less than zero.")
        super().save(*args, **kwargs)

    # def get_booked_seats_by_passenger(self, passenger):
    #     bookings = Booking.objects.filter(vehicle=self, passenger=passenger)
    #     total_booked_seats = sum(booking.num_passengers for booking in bookings)
    #     return total_booked_seats

    def __str__(self):
        return f"{self.registration_number} - {self.company_made} {self.model}"


class Trip(models.Model):
    trip_id = models.CharField(max_length=100, unique=True, default="JNKKTM")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_query_name="trip_organization")
    from_location = models.CharField(max_length=100)
    to_location = models.CharField(max_length=100)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    def save(self, *args, **kwargs):
        prefix = f"{self.from_location[:3]}{self.to_location[:3]}"
        timestamp = prefix + timezone.now().strftime("%Y%m%d%H%M%S")
        self.trip_id = timestamp.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.trip_id} - {self.start_datetime}"


class TripPrice(models.Model):
    trip_price_id = models.CharField(max_length=100, unique=True, default="POKKATABC123")
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        prefix = f"{self.trip.trip_id}{self.vehicle.registration_number}"
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        self.trip_price_id = timestamp.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Trip from {self.trip.from_location} to {self.trip.to_location} - Price ID: {self.trip_price_id} - Price: {self.price}"


def generate_ticket_content(booking):
    ticket_content = f"""
        -------------------------------------
        Booking ID: {booking.booking_id}
        Passenger: {booking.passenger.user.username}
        Trip: {booking.tripprice.trip.from_location} to {booking.tripprice.trip.to_location}
        No. of Passengers: {booking.num_passengers}
        Price per Person: {booking.tripprice.price}
        Total Price: {booking.price}
        Trip Date: {booking.tripprice.trip.start_datetime.strftime("%Y-%m-%d %H:%M:%S")}
        Ticket Booked Time: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}
        -------------------------------------
    """
    return ticket_content


class Booking(models.Model):
    booking_id = models.CharField(max_length=200, unique=True, default="passenger2JANKATXYZ1234")
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    tripprice = models.ForeignKey(TripPrice, on_delete=models.CASCADE)
    num_passengers = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def clean(self):
        if self.num_passengers > self.tripprice.vehicle.available_seat:
            raise serializers.ValidationError("Not enough available seats in the vehicle.")

    def save(self, *args, **kwargs):
        print("vehicle available seat",self.tripprice.vehicle.available_seat)   
        self.clean()
        self.price = self.tripprice.price * self.num_passengers
        self.tripprice.vehicle.available_seat -= self.num_passengers
        self.tripprice.vehicle.save()
        print("=====================================")
        print("trip price",self.tripprice)
        print("trip price",self.price)
        print("trip price vehicle",self.tripprice.vehicle.available_seat)
        print("trip price vehicle",self.tripprice.vehicle.seating_capacity)
        print("=====================================")

        prefix = f"{self.passenger.user.username}_{self.num_passengers}_{self.tripprice.trip_price_id}"
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        self.booking_id = f"{prefix}_{timestamp}".upper()
        super().save(*args, **kwargs)

        ticket_content = generate_ticket_content(self)
        filename = f"{self.booking_id}.txt"
        ticket_file_path = os.path.join(settings.MEDIA_ROOT, 'tickets', filename)
        print("ticket file path",ticket_file_path)

        try:
            with open(ticket_file_path, 'w+') as ticket_file:
                ticket_file.write(ticket_content)
        except Exception as e:
            raise serializers.ValidationError(f"Error creating ticket file: {str(e)}")

        Ticket.objects.create(booking=self, ticket_file=ticket_file_path)

    def __str__(self):
        return f"Booking for {self.passenger.user.username} on {self.tripprice.vehicle.registration_number} - {self.tripprice.trip.from_location} to {self.tripprice.trip.to_location}"


class Ticket(models.Model):
    ticket_id = models.CharField(max_length=200, unique=True, default="passenger2JANKATXYZ1234")
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    ticket_file = models.FileField()
    
    def save(self, *args, **kwargs):
        prefix = f"{self.booking.passenger.user.username}_{self.booking.num_passengers}_{self.booking.tripprice.trip_price_id}"
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        self.ticket_id = f"{prefix}_{timestamp}".upper()
        super().save(*args, **kwargs )
        

    def __str__(self):
        return f"Ticket for {self.booking.tripprice.vehicle.registration_number} - {self.booking.tripprice.trip.from_location} to {self.booking.tripprice.trip.to_location}"
