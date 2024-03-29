from django.db import models


class SeatStatus(models.TextChoices):
    INITIAL = "INITIAL"
    FREE = "FREE"
    RESERVED = "RESERVED"
    PROBLEM = "PROBLEM"


class AbstractSeat(models.Model):
    number = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=10, choices=SeatStatus.choices, default=SeatStatus.FREE)
    price = models.PositiveBigIntegerField(default=0, blank=True)
    is_valid = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
