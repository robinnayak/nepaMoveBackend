from django.db import models
from authentication.models import CustomUser
# Create your models here.
CHOICES = [
    ('en','English'),
    ('ne','Nepali'),
]
class Passenger(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE, related_query_name='user_passenger')
    phone_number = models.CharField(max_length=15,blank=True)
    address = models.CharField(max_length=255,blank=True)

    emergency_contact_name = models.CharField(max_length=50,blank=True)
    emergency_contact_number = models.CharField(max_length=10,blank=True)
    date_of_birth = models.DateField(blank=True,null=True)
    preferred_language = models.CharField(max_length=20,choices = CHOICES,blank=True)
    
    def __str__(self) -> str:
        return self.user.username
