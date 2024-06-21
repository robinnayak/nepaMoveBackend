from django.urls import path
from . import views
from authentication.views import  OrganizationDetailView
urlpatterns = [
    path('',OrganizationDetailView.as_view(), name='organization'),
]
