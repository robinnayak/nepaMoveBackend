from django.urls import path
from . import views
from authentication.views import RegistrationView,LoginView,LogoutView
urlpatterns = [
    path('', views.index, name='home'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/',LogoutView.as_view(), name='logout'),
       
]
