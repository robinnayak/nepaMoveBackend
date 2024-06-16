from django.urls import path
from . import views
from authentication.views import  OrganizationDetailView,RegistrationView,LoginView,LogoutView,OrganizationView,DriverDetailView
urlpatterns = [
    path('', views.index, name='home'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/',LogoutView.as_view(), name='logout'),
    path('organizations/',OrganizationView.as_view(), name='organizations'),
    path('organizations/<int:pk>/',OrganizationDetailView.as_view(), name='organization'),
    path('driver/<int:pk>/',DriverDetailView.as_view(), name='drivers'),
]
