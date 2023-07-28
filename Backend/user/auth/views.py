from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token


from user.auth.serializers import LoginSerializer
from user.models import User
from user.permissions import IsAnonymous

class LoginUserAPIView(generics.CreateAPIView):
    
    queryset = User.objects.all()
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        if request.data.get('email') and request.data.get('password'):
            email = request.data['email']
            password = request.data["password"]
            try:
                user = authenticate(email=email, password=password)
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                #user = User.objects.create_user(email=email)
            # token, created = Token.objects.get_or_create(user=user)
            refresh = RefreshToken.for_user(user)
            context = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(context)
            # raise AuthenticationFailed("{} invalid password".format(request.data["password"]))

        else:
            data = {"error": "phone and password fields required"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
