from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext as _
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.models import User, UserAddress
from user.permissions import IsOwner, IsAnonymous, IsOwnerOrReadOnly
from user.serializers import UserSerializer, AddressSerializer,SignupSerializer

#TODO change info
class DetailUserAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwner]
    authentication_classes = [JWTAuthentication]
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):

        if self.request.data.get('gender'):
            self.request.data._mutable = True
            self.request.data['gender'] = self.request.data['gender'].upper()
            self.request.data._mutable = False

        return super(DetailUserAPIView, self).get_queryset()

    def perform_destroy(self, instance):
        instance.is_valid = False
        instance.save()


class DetailAddressAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsOwner]
    authentication_classes = [JWTAuthentication]
    throttle_classes = [UserRateThrottle]

    def get_object(self):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, user)
        return get_object_or_404(UserAddress, phone=user.phone)

class Signup(APIView):
    # permission_classes = [IsAnonymous,IsOwner,IsOwnerOrReadOnly]
    serializer_class = SignupSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            phone = serializer.data['phone']
            email = serializer.data['email']
            password = serializer.data['password']
            pass_repeat = serializer.data['pass_repeat']

            try:
                user = get_user_model().objects.get(email=email)
                if user.is_verified:
                    content = {'detail': _('Email address already taken.')}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                if password != pass_repeat:
                    return Response('unmatch Passwords',status=status.HTTP_400_BAD_REQUEST)

            except get_user_model().DoesNotExist:
                user = get_user_model().objects.create_user(email=email, phone = phone)

            # Set user fields provided
            user.set_password(password)
            user.phone = phone
            user.email = email
            user.save()

            content = {'email': email, 'phone': phone,}
            return Response(content, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
