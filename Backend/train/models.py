from user.base_models.address import AbstractAddress
from reservation.base_models.passenger import AbstractPassenger, TransferStatus
from reservation.base_models.rate import AbstractRate
from reservation.base_models.reservation import AbstractReservation
from reservation.base_models.seat import AbstractSeat
from reservation.base_models.transport import *

# ---------------------------------------------Railway------------------------------------------------------------------

class railwayAddress(AbstractAddress):
    pass

class Railway_station(AbstractTransport):
    address = models.ForeignKey(railwayAddress, on_delete=models.PROTECT, related_name='Railway_station')
    
    def __str__(self):
        return "{}".format(self.title)


# ---------------------------------------------Train-----------------------------------------------------------------

class Train(AbstractTransfer):
    source = models.ForeignKey(Railway_station, on_delete=models.PROTECT,
                               related_name='source')
    destination = models.ForeignKey(Railway_station, on_delete=models.PROTECT,
                                    related_name='destination')

    @property
    def price_per_seat(self):
        price = TrainSeat.objects.filter(Train=self).first()
        return price.price or -1

    def __str__(self):
        return "{} : {}".format(self.source.title, self.transport_number)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        ordering = ['-transport_number']
        
# ---------------------------------------------TrainSeat-------------------------------------------------------------

class TrainSeat(AbstractSeat):
    Train = models.ForeignKey(Train, related_name='seat', on_delete=models.CASCADE)

    def __str__(self):
        return "{}: {}".format(self.price, self.number)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=('Train', 'number'), name='unique_Train_seat')]


# ---------------------------------------------Passengers-------------------------------------------------------------

class TrainPassenger(AbstractPassenger):
    seat = models.ForeignKey(TrainSeat, related_name='seat', on_delete=models.CASCADE)
    transfer_status = models.CharField(max_length=20, choices=TransferStatus.choices, default=TransferStatus.INITIAL)

    def __str__(self):
        return "{}: {} - {} -> {}".format(self.seat.Train.source.title
                                          , self.seat.Train.transport_number, self.seat.number, self.national_id)

    class Meta:
        constraints = [models.UniqueConstraint(
            condition=models.Q(
                transfer_status__in=[TransferStatus.INITIAL, TransferStatus.RESERVED, TransferStatus.TRANSFER])
            , fields=('seat', 'national_id'), name='unique_TrainSeat_user')]


# ---------------------------------------------TrainReservation------------------------------------------------------

class TrainReservation(AbstractReservation):
    Train = models.ForeignKey(Train, on_delete=models.PROTECT, related_name="Train_reservation")
    passenger_count = models.PositiveSmallIntegerField()

    def __str__(self):
        return "{} - {} - {}".format(self.Train.source,
                                     self.Train.transport_number,self.Train.destination)



