from django.urls import path,include
from . import views
from authentication.views import  OrganizationDetailView,RegistrationView,LoginView,LogoutView,OrganizationView,DriverDetailView
from organization.views import VehicleView
urlpatterns = [
    path('', views.index, name='home'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/',LogoutView.as_view(), name='logout'),
    path('organization/',include('organization.urls'), name='organizationss'),
    # path('vehicle/',VehicleView.as_view(), name='vehicle' ),
    # path('vehicle/',VehicleView.as_view(), name='vehicle' ),
    # path('vehicle/',VehicleView.as_view(), name='vehicle' ),
    
    
    path('driver/<int:pk>/',include('driver.urls'), name='driver'),
]
