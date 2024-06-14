from django.contrib import admin
from .models import CustomUser, Organization, Driver

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Organization)
admin.site.register(Driver)


