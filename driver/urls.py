from django.urls import path
from . import views
from authentication.views import  DriverDetailView
urlpatterns = [
    path('',DriverDetailView.as_view(), name='drivers'),
]
