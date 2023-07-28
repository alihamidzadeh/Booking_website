from rest_framework_simplejwt.views import TokenObtainPairView

from user.auth.token_obtain.serializers import TokenAPISerializer


class TokenAPIView(TokenObtainPairView):
    serializer_class = TokenAPISerializer