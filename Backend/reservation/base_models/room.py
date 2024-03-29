from django.db import models


class RoomStatus(models.TextChoices):
    INITIAL = "INITIAL"
    FREE = "FREE"
    RESERVED = "RESERVED"
    PROBLEM = "PROBLEM"


class AbstractRoom(models.Model):
    number = models.PositiveSmallIntegerField()
    capacity = models.PositiveSmallIntegerField()
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=RoomStatus.choices, default=RoomStatus.FREE)
    price = models.PositiveBigIntegerField(blank=True)
    is_valid = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
