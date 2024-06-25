from django.urls import path
from . import views
from authentication.views import  OrganizationDetailView,OrganizationView
urlpatterns = [
    path("",  OrganizationView.as_view(), name="org"),
    path('<int:pk>/',OrganizationDetailView.as_view(), name='organization'),
    path('vehicle/',views.VehicleView.as_view(), name='vehicle' ),
    path('vehicle/<str:reg_id>/',views.VehicleDetailView.as_view(), name='vehicle_detail' ),
    path('trip/',views.TripView.as_view(), name='trip' ),
    path('trip/<str:trip_id>/',views.TripDetailView.as_view(), name='trip_detail' ),
    path('tripprice/',views.TripPriceView.as_view(), name='tripprice' ),
    path('tripprice/<str:trip_price_id>/',views.TripPriceDetailView.as_view(), name='tripprice_detail' ),
    path('booking/',views.BookingView.as_view(), name='booking' ),
    path('booking/<str:booking_id>/',views.BookingDetailView.as_view(), name='booking_detail' ),
    path('ticket/',views.TicketView.as_view(), name='ticket' ),
    path('ticket/<str:ticket_id>/',views.TicketDetailView.as_view(), name='ticket_detail' ),

]
