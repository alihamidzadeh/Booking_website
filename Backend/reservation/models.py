from django.db import models

from django.conf import settings

from user.base_models.address import AbstractAddress
from reservation.base_models.rate import AbstractRate
from reservation.base_models.reservation import AbstractReservation
from reservation.base_models.residence import AbstractResidence
from reservation.base_models.transport import *


class PaymentStatus(models.TextChoices):
    INITIAL = "INITIAL"
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='user')
    payment_status = models.CharField(max_length=15, choices=PaymentStatus.choices, default=PaymentStatus.INITIAL)
    reserved_key = models.CharField(max_length=100, unique=True)
    price = models.IntegerField(blank=True,default=0)

    is_valid = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.reserved_key
