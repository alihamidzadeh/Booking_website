from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from user.models import User, UserAddress


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = ('id', 'phone', 'address',)
        read_only_fields = ('id', "phone",)


class UserSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'phone', 'email', 'birth_day', 'gender',
                  'address')
        read_only_fields = ("id", "email",)

    def to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['gender'] = obj.get_gender_display().upper() if obj.gender else None
        query_address = UserAddress.objects.filter(phone=obj.phone)
        ret['address'] = AddressSerializer(query_address.first()).data if query_address.exists() else None
        return ret

    def update(self, instance, validated_data):
        user_email = User.objects.filter(email=validated_data.get('email')).exclude(id=instance.id).exists()
        if user_email:
            raise ValidationError("This email existed !!")
        return super(UserSerializer, self).update(instance, validated_data)


class SignupSerializer(serializers.Serializer):
    firstname = serializers.CharField(max_length=20, required=True)
    lastname = serializers.CharField(max_length=20, required=True)
    phone = serializers.CharField(max_length=20, required=True)
    email = serializers.EmailField(max_length=255, required=True)
    password = serializers.CharField(max_length=128, required=True)
    pass_repeat = serializers.CharField(max_length=128, required=True)
