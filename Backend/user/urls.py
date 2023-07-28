from django.urls import path, include
from user.views import DetailUserAPIView, DetailAddressAPIView, Signup

urlpatterns = [
    path('signup/', Signup.as_view(), name='SignUp'),
    path('api/user/<int:pk>/', DetailUserAPIView.as_view(), name='user-detail'),
    path('api/user/<int:pk>/address/', DetailAddressAPIView.as_view(), name='address-detail'),
    path('', include('user.auth.urls')),
]
