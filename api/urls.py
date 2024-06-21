from django.urls import path,include
from . import views
from authentication.views import  OrganizationDetailView,RegistrationView,LoginView,LogoutView,OrganizationView,DriverDetailView
urlpatterns = [
    path('', views.index, name='home'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/',LogoutView.as_view(), name='logout'),
    path('organizations/',OrganizationView.as_view(), name='organizations'),
    path('organizations/<int:pk>/',include('organization.urls'), name='organizationss'),
    path('driver/<int:pk>/',include('driver.urls'), name='driver'),
]
