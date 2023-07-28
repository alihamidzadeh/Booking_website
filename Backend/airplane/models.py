from user.base_models.address import AbstractAddress
from reservation.base_models.passenger import AbstractPassenger, TransferStatus
from reservation.base_models.rate import AbstractRate
from reservation.base_models.reservation import AbstractReservation
from reservation.base_models.seat import AbstractSeat
from reservation.base_models.transport import *
from django.core.exceptions import ValidationError


# ---------------------------------------------AirplaneAddress----------------------------------------------------------

class AirportAddress(AbstractAddress):
    pass
# ---------------------------------------------Airport------------------------------------------------------------------


class Airport(AbstractTransport):
    address = models.ForeignKey(AirportAddress, on_delete=models.PROTECT, related_name='airport')


# class AirportTerminal(AbstractTerminal):
#     airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="airport")

#     def __str__(self):
#         return "{} : {}".format(self.airport.title, self.number)


class AirplaneCompany(AbstractTransportCompany):
    pass

    @property
    def average_rating(self):
        rate = AirplaneCompanyRating.objects.filter(company=self).all().aggregate(avg=models.Avg('rate'))
        return rate.get('avg') or 5

    def __str__(self):
        return "{}".format(self.name)


# ---------------------------------------------Airplane-----------------------------------------------------------------

class Airplane(AbstractTransfer):
    company = models.ForeignKey(AirplaneCompany, on_delete=models.CASCADE, related_name="airplane")
    pilot = models.CharField(max_length=50)
    source = models.ForeignKey(Airport, on_delete=models.PROTECT,
                               related_name='source')
    destination = models.ForeignKey(Airport, on_delete=models.PROTECT,
                                    related_name='destination')
    
    @property
    def average_rating(self):
        rate = AirplaneCompanyRating.objects.filter(company__airplane=self).all().aggregate(avg=models.Avg('rate'))
        return rate.get('avg') or 5

    @property
    def price_per_seat(self):
        price = AirplaneSeat.objects.filter(airplane=self).first()
        return price.price or -1

    def __str__(self):
        return "{} : {}".format(self.company.name, self.transport_number)
    def check_dates(self):
        if super().back_date < super().transfer_date:
            raise ValidationError
        return 
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.pilot = self.pilot.title()

        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        ordering = ['-transport_number']
        constraints = [models.UniqueConstraint(
            condition=models.Q(
                transport_status__in=[TransportStatus.SPACE, TransportStatus.TRANSFER]),
            fields=('pilot', 'transport_status'), name='unique_pilot_transport_status')]


# ---------------------------------------------AirplaneSeat-------------------------------------------------------------

class AirplaneSeat(AbstractSeat):
    airplane = models.ForeignKey(Airplane, related_name='seat', on_delete=models.CASCADE)

    def __str__(self):
        return "{}: {}".format(self.airplane.company.name, self.number)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=('airplane', 'number'), name='unique_airplane_seat')]


# ---------------------------------------------Passengers-------------------------------------------------------------

class AirplanePassenger(AbstractPassenger):
    seat = models.ForeignKey(AirplaneSeat, related_name='seat', on_delete=models.CASCADE)
    transfer_status = models.CharField(max_length=20, choices=TransferStatus.choices, default=TransferStatus.INITIAL)

    def __str__(self):
        return "{}: {} - {} -> {}".format(self.seat.airplane.company.name
                                          , self.seat.airplane.transport_number, self.seat.number, self.national_id)

    class Meta:
        constraints = [models.UniqueConstraint(
            condition=models.Q(
                transfer_status__in=[TransferStatus.INITIAL, TransferStatus.RESERVED, TransferStatus.TRANSFER])
            , fields=('seat', 'national_id'), name='unique_FlightSeat_user')]


# ---------------------------------------------AirplaneReservation------------------------------------------------------

class AirplaneReservation(AbstractReservation):
    airplane = models.ForeignKey(Airplane, on_delete=models.PROTECT, related_name="airplane_reservation")
    passenger_count = models.PositiveSmallIntegerField()

    def __str__(self):
        return "{} - {} - {}".format(self.airplane.company.name,
                                     self.airplane.transport_number,self.airplane.destination)


# ---------------------------------------------AirplaneRate-------------------------------------------------------------

class AirplaneCompanyRating(AbstractRate):
    company = models.ForeignKey(AirplaneCompany, on_delete=models.CASCADE, related_name='rate')

    def __str__(self):
        return "{} got {} from {}".format(self.company.name, self.rate, self.user.phone)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=('company', 'user'), name='unique_company_user')]





