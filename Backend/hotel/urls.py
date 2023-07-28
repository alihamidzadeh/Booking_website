from django.urls import path

from hotel.views import *

urlpatterns = [
    path('hotel/', ListCreateHotelAPIView.as_view(), name='hotel'),
    path('hotel/<str:name>/', DetailHotelAPIView.as_view(), name='hotel-detail'),

    path('hotel/<str:name>/room/', ListCreateHotelRoomAPIView.as_view(), name='hotel-room'),
    path('hotel/<str:name>/room/<int:number>/', DetailHotelRoomAPIView.as_view(), name='hotel-room-detail'),

    path('hotel/<str:name>/room/<int:number>/inital/', CreateHotelReservationAPIView.as_view(),
         name='hotel-reserved'),
    path('hotel/reserved/<str:reserved_key>/', DetailHotelReservationAPIView.as_view(),
         name='hotel-reserved-detail'),
    path('hotel/payment/<str:reserved_key>/reserving/', PaymentReservationAPIView.as_view(),
         name='hotel-payment-result'),

    path('hotel/<str:name>/rate/', CreateHotelRateAPIView.as_view(), name='hotel-rate'),
    path('hotel/<str:name>/rating/<int:pk>/', DetailHotelRateAPIView.as_view(), name='hotel-rate-detail'),

]
