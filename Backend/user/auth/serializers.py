from rest_framework import serializers

from user.models import User


# class OTPSerializer(serializers.Serializer):
#     otp = serializers.CharField(max_length=5)

#     def update(self, instance, validated_data):
#         pass

#     def create(self, validated_data):
#         pass


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email','password')

    def create(self, validated_data):
        user = User.objects.create(email=validated_data.get('email'))
        return user
