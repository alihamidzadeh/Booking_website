from django.db import transaction
from rest_framework import serializers

from reservation.models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'user', 'payment_status', 'reserved_key','price')
