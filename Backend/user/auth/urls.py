from django.urls import path

from user.auth.token_obtain.views import TokenAPIView
from user.auth.views import LoginUserAPIView

urlpatterns = [
    path('user/login/', LoginUserAPIView.as_view(), name='user-login'),

    path('api/token/', TokenAPIView.as_view(), name='token_obtain'),
]
