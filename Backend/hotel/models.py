from django.db import models

# Create your models here.
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from user.base_models.address import AbstractAddress
from reservation.base_models.passenger import AbstractPassenger, StayStatus
from reservation.base_models.room import AbstractRoom
from reservation.base_models.rate import AbstractRate
from reservation.base_models.reservation import AbstractReservationResidence, ReservedStatus
from reservation.base_models.residence import AbstractResidence

# ---------------------------------------------Hotel--------------------------------------------------------------------

class Hotel(AbstractResidence):
    star = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=3)
    room_count = models.PositiveSmallIntegerField(default=100)
    address = models.OneToOneField('HotelAddress', on_delete=models.PROTECT, related_name='hotel_address')
    avatar = models.ImageField(upload_to="", null=True, blank=True)


    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.name = self.name.title()
        self.description = self.description.capitalize()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        rate = HotelRating.objects.filter(hotel=self).all().aggregate(avg=models.Avg('rate'))
        return rate.get('avg') or 5

    # @property
    # def price_per_night(self):
    #     price = HotelRoom.objects.filter(hotel=self).first()
    #     return price.price or -1

    class Meta:
        ordering = ['-star']
        constraints = [models.UniqueConstraint(fields=('name', 'residence_status'),
                                               name='unique_hotel_name_residence_status')]


# ----------------------------------------------HotelRoom---------------------------------------------------------------

class HotelRoom(AbstractRoom):
    hotel = models.ForeignKey(Hotel, related_name='room', on_delete=models.CASCADE)
    room_avatar = models.ImageField(upload_to="", null=True, blank=True)

    def __str__(self):
        return "{}: {}".format(self.hotel.name, self.number)

    class Meta:
        ordering = ["price"]
        constraints = [models.UniqueConstraint(
            fields=('hotel', 'number'), name='unique_hotel_number_seat')]


# -----------------------------------------------Passengers-------------------------------------------------------------


class HotelPassenger(AbstractPassenger):
    room = models.ForeignKey(HotelRoom, related_name='room', on_delete=models.CASCADE)
    stay_status = models.CharField(max_length=20, choices=StayStatus.choices, default=StayStatus.INITIAL)

    def __str__(self):
        return "{}: {} -> {}".format(self.room.hotel.name, self.room.number, self.national_id)


# ----------------------------------------------HotelReservation--------------------------------------------------------


class HotelReservation(AbstractReservationResidence):
    room = models.ForeignKey(HotelRoom, on_delete=models.PROTECT, related_name="reservation")

    def __str__(self):
        return "{} - {} -> from:{} - to:{}".format(self.user.phone, self.room.hotel.name, self.check_in_date,
                                                   self.check_out_date)

    class Meta:
        constraints = [models.UniqueConstraint(
            condition=models.Q(reserved_status__in=[ReservedStatus.INITIAL, ReservedStatus.RESERVED]),
            fields=('user', 'room'), name='unique_user_hotel_room')]


# ----------------------------------------------HotelRate---------------------------------------------------------------

class HotelRating(AbstractRate):
    hotel = models.ForeignKey(Hotel, related_name='rate', on_delete=models.CASCADE)

    def __str__(self):
        return "{} : {}".format(self.hotel.name, self.hotel.rate)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=('hotel', 'user', 'rate'), name='unique_hotel_user_rate')]


# ----------------------------------------------HotelAddress------------------------------------------------------------


class HotelAddress(AbstractAddress):
    country = models.CharField(blank=True, null=True, max_length=50)
    city = models.CharField(blank=True, null=True, max_length=50)

    def __str__(self):
        return "{} : {}".format(self.country, self.city)

