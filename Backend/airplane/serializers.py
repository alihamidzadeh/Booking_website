from django.db import transaction, IntegrityError
from django.utils import timezone
from rest_framework import serializers, exceptions

from airplane.models import *
from reservation.base_models.passenger import PassengerType
from reservation.base_models.reservation import ReservedStatus
from reservation.base_models.seat import SeatStatus
from reservation.models import PaymentStatus, Payment
from reservation.serializers import PaymentSerializer
from utlis.calc_age import calc_age
from utlis.check_obj import check_reserved_key_existed, check_status_in_request_data
from utlis.reservation import convert_payment_status_to_reserved_status


# ---------------------------------------------AirportAddress-----------------------------------------------------------

class AirportAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = AirportAddress
        fields = ('id', 'phone', 'address',)
        extra_kwargs = {'phone': {'required': False}}


# ---------------------------------------------Airport------------------------------------------------------------------

class AirportSerializer(serializers.ModelSerializer):
    address = AirportAddressSerializer(many=False)

    class Meta:
        model = Airport
        fields = ('id', 'title', 'address',)

class AirplaneCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneCompany
        fields = ('id', 'name',)


# ---------------------------------------------AirplaneCompanyRating-----------------------------------------------------

class AirplaneCompanyRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneCompanyRating
        fields = ('id', 'company', 'user', 'rate',)


# ---------------------------------------------Airplane-----------------------------------------------------------------


class AirplaneSerializer(serializers.ModelSerializer):
    company = serializers.SlugRelatedField(slug_field='name', many=False, read_only=True)
    source = AirportSerializer(many=False, read_only=True, required=False)
    destination = AirportSerializer(many=False, read_only=True, required=False)
    class Meta:
        model = Airplane
        fields = (
            'id', 'pilot', 'company', 'average_rating', 'price_per_seat', 'transport_number', 'description',
            'transport_status', 'max_reservation', 'number_reserved', 'source', 'back_date', 'destination',
            'transfer_date',)
        extra_kwargs = {"transport_number": {"required": False, "read_only": True}}


# ---------------------------------------------AirportSeat--------------------------------------------------------------

class AirplaneSeatSerializer(serializers.ModelSerializer):

    class Meta:
        model = AirplaneSeat
        fields = ('id', 'number', 'status', 'price', 'airplane')


# ---------------------------------------------AirplanePassenger--------------------------------------------------------

class AirplanePassengerSerializer(serializers.ModelSerializer):
    seat = AirplaneSeatSerializer(required=False)

    class Meta:
        model = AirplanePassenger
        fields = (
            'id', 'passenger_code', 'parent', 'seat', 'phone', 'national_id', 'birth_day', 'first_name', 'last_name',
            'transfer_status', 'passenger_type',)

        extra_kwargs = {"parent": {'required': False}}


# ---------------------------------------------AirplaneReservation------------------------------------------------------

class AirplaneReservationSerializer(serializers.ModelSerializer):
    total_cost = serializers.SerializerMethodField()
    payment = PaymentSerializer(many=False, required=False)
    passenger = AirplanePassengerSerializer(many=True, required=False)

    class Meta:
        model = AirplaneReservation
        fields = ('id', 'airplane', 'user', 'reserved_status', 'passenger_count', 'total_cost',
                  'payment', 'passenger',)

    def get_total_cost(self, obj):
        return {"cost": obj.passenger_count * obj.airplane.price_per_seat}

    def validate(self, data):
        if (data["airplane"].max_reservation - data["airplane"].number_reserved) < data["passenger_count"]:
            raise exceptions.ValidationError({
                "passenger_count": "Seat has {} capacity for this airplane number: {}!".format(
                    (data["airplane"].max_reservation - data["airplane"].number_reserved),
                    data["airplane"].transport_number)})
        return data

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        payment = Payment.objects.filter(reserved_key=instance.reserved_key).get()
        ret['payment'] = PaymentSerializer(payment).data

        passengers = AirplanePassenger.objects.filter(reserved_key=instance.reserved_key).all()
        ret['passengers'] = AirplanePassengerSerializer(passengers, many=True).data
        return ret

    @transaction.atomic
    def create(self, validated_data):
        airplane = validated_data['airplane']
        passengers = validated_data.pop('passenger', None)
        if len(passengers) != validated_data['passenger_count']:
            raise exceptions.ValidationError("passenger information uncompleted!")

        seats = AirplaneSeat.objects.filter(airplane_id=airplane, status=SeatStatus.FREE) \
            .order_by('number').all()
        if validated_data['passenger_count'] > seats.count():
            raise exceptions.ValidationError("not enough seats!")

        try:
            reserve = AirplaneReservation.objects.create(**validated_data)
            Payment.objects.create(user=reserve.user, reserved_key=reserve.reserved_key)
            update_seats = []
            create_passengers = []
            for passenger, seat in zip(passengers, seats):
                seat.status = SeatStatus.INITIAL
                update_seats.append(seat)
                _passenger = AirplanePassenger(seat=seat, reserved_key=reserve.reserved_key,
                                               parent=validated_data['user'], **passenger)
                if calc_age(passenger['birth_day']) < 18:
                    _passenger.passenger_type = PassengerType.CHILDREN

                create_passengers.append(_passenger)

            AirplanePassenger.objects.bulk_create(create_passengers)
            AirplaneSeat.objects.bulk_update(update_seats, fields=["status"])

            airplane.number_reserved += len(passengers)
            airplane.save()

        except (ValueError, TypeError) as e:
            raise exceptions.ValidationError("invalid data -> {}".format(e))
        except IntegrityError as e:
            raise exceptions.ValidationError("Each user has only one record reserved seat!")
        except Exception as e:
            raise exceptions.ValidationError("Error: {}".format(e))
        return reserve

    @transaction.atomic
    def update(self, instance, validated_data):
        reserved_key = instance.reserved_key

        passengers = validated_data.pop('passenger', None)

        if instance.passenger_count != validated_data['passenger_count']:
            raise exceptions.ValidationError("passenger information uncompleted!")

        old_passengers = AirplanePassenger.objects.filter(
            reserved_key=reserved_key, transfer_status=TransferStatus.INITIAL).all()

        try:
            for passenger in passengers:
                update_passenger = old_passengers.filter(national_id=passenger['national_id'])
                if update_passenger.exists():
                    update_passenger.update(**passenger)
                else:
                    raise exceptions.ValidationError("Passenger info not existed")

        except (ValueError, TypeError) as e:
            raise exceptions.ValidationError("invalid data -> {}".format(e))
        except IntegrityError as e:
            raise exceptions.ValidationError("Each user has only one record reserved seat!")
        except Exception as e:
            raise e

        return instance


@transaction.atomic
def cancel_airplane_reservation(instance):
    airplane = instance.airplane

    try:
        payment = Payment.objects.filter(reserved_key=instance.reserved_key, payment_status=PaymentStatus.SUCCESS).get()
        passengers = AirplanePassenger.objects.filter(reserved_key=instance.reserved_key,
                                                      transfer_status=TransferStatus.RESERVED).all()

        if instance.reserved_status == ReservedStatus.RESERVED and payment \
                and passengers.count() == instance.passenger_count:

            payment.payment_status = PaymentStatus.CANCELLED
            payment.save()

            instance.reserved_status = ReservedStatus.CANCELLED
            instance.save()

            update_passengers = []
            update_seats = []
            for passenger in passengers:
                if passenger.transfer_status == TransferStatus.RESERVED:
                    passenger.transfer_status = TransferStatus.CANCELLED
                    update_passengers.append(passenger)

                else:
                    raise exceptions.ValidationError("This passenger :{} transfer_status invalid".format(passenger.id))

                if passenger.seat.status == SeatStatus.RESERVED:
                    passenger.seat.status = SeatStatus.FREE
                    update_seats.append(passenger.seat)
                else:
                    raise exceptions.ValidationError("This seat :{} seat status invalid".format(passenger.seat.id))

            AirplanePassenger.objects.bulk_update(update_passengers, fields=['transfer_status'])
            AirplaneSeat.objects.bulk_update(update_seats, fields=['status'])

            airplane.number_reserved -= instance.passenger_count
            if airplane.transport_status == TransportStatus.FULL:
                airplane.transport_status = TransportStatus.SPACE
            airplane.save()

        else:
            raise exceptions.ValidationError(
                "This instance :{} reserved_status invalid".format(instance.reserved_status))

    except (ValueError, TypeError) as e:
        raise exceptions.ValidationError("invalid data -> {}".format(e))
    except Exception as e:
        raise exceptions.ValidationError("Error: {}".format(e))


# ---------------------------------------------ResultReservation-------------------------------------------------------

@transaction.atomic
def update_reservation(request, **kwargs):
    reserved_key = kwargs['reserved_key']
    payment_status = check_status_in_request_data('payment_status', request.data, PaymentStatus)

    # reserve -> change ,payment -> change, room -> change
    try:
        reserve = check_reserved_key_existed(reserved_key, AirplaneReservation)
        if reserve.reserved_status == ReservedStatus.INITIAL:
            reserved_status = convert_payment_status_to_reserved_status(payment_status)
            reserve.reserved_status = reserved_status
            reserve.save()
        else:
            raise exceptions.ValidationError("This reserved: {} not initial".format(reserved_key))

        payment = check_reserved_key_existed(reserved_key, Payment)
        if payment.payment_status in [PaymentStatus.INITIAL, PaymentStatus.FAILED]:
            payment.payment_status = payment_status
            payment.save()
        else:
            raise exceptions.ValidationError("Payment for this reserved: {} was invalid".format(reserved_key))

        passengers = check_reserved_key_existed(reserved_key, AirplanePassenger, True)
        if reserved_status == ReservedStatus.RESERVED:
            passengers_update = []
            seats_update = []
            for passenger in passengers:
                if passenger.transfer_status == TransferStatus.INITIAL:
                    passenger.transfer_status = TransferStatus.RESERVED
                    passengers_update.append(passenger)

                    passenger.seat.status = SeatStatus.RESERVED
                    seats_update.append(passenger.seat)
                else:
                    raise exceptions.ValidationError(
                        "Passenger info for this reserved: {} was invalid".format(reserved_key))

            AirplanePassenger.objects.bulk_update(passengers_update, fields=['transfer_status'])
            AirplaneSeat.objects.bulk_update(seats_update, fields=['status'])
            check_and_update_if_airplane_full(reserve.airplane_id)

    except IntegrityError as e:
        raise exceptions.ValidationError("Error: {}".format(e))
    except (ValueError, TypeError) as e:
        raise exceptions.ValidationError("invalid data -> {}".format(e))

    return {"reserve": AirplaneReservationSerializer(reserve).data}


def check_and_update_if_airplane_full(airplane_id):
    try:
        airplane = Airplane.objects.filter(id=airplane_id, transport_status=TransportStatus.SPACE,
                                           transfer_date__gt=timezone.now(), is_valid=True).get()
        if airplane.number_reserved == airplane.max_reservation:
            airplane.transport_status = TransportStatus.FULL
        return airplane.save()
    except Airplane.DoesNotExist:
        raise exceptions.ValidationError("Airplane Dose not exist fot this id: {}!".format(airplane_id))


