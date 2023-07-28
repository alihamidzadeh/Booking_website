from django.urls import path
from train.views import *

urlpatterns = [
    path('Train/', ListTrainAPIView.as_view(), name='Train'),
    path('Train/<int:pk>/', DetailTrainAPIView.as_view(), name='Train-detail'),

    path('Train/<int:pk>/seat/', ListTrainSeatAPIView.as_view(), name='Train-seat'),

    path('Train/<int:pk>/inital/', CreateTrainReservationAPIView.as_view(),
         name='Train-reserved'),
    path('Train/reserved/<str:reserved_key>/', DetailTrainReservationAPIView.as_view(),
         name='Train-reserved-detail'),
    path('Train/payment/<str:reserved_key>/reserving/', PaymentReservationAPIView.as_view(),
         name='Train-payment-result'),

]
