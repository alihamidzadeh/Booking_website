from django.shortcuts import render
from django.shortcuts import render
from rest_framework import generics, response, status, filters
from rest_framework.permissions import IsAdminUser, AllowAny, SAFE_METHODS, IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework_simplejwt.authentication import JWTAuthentication

from train.serializers import *
from user.permissions import IsOwner


class TrainMixin:
    authentication_classes = [JWTAuthentication]
    throttle_classes = [UserRateThrottle]

    def get_train(self, pk, is_valid=True):
        try:
            return Train.objects.filter(
                pk=pk, transport_status=TransportStatus.SPACE, transfer_date__gt=timezone.now(),
                is_valid=is_valid).get()
        except Train.DoesNotExist:
            raise exceptions.ValidationError("Train Dose not exist fot this id: {}!".format(pk))

    def get_reservation(self, reserved_key, is_valid):
        try:
            if is_valid:
                return TrainReservation.objects.filter(reserved_key=reserved_key, is_valid=is_valid).get()
            return TrainReservation.objects.filter(reserved_key=reserved_key).get()
        except TrainReservation.DoesNotExist:
            raise exceptions.ValidationError("This reserved Dose not exist with this key: {}!".format(reserved_key))

    def get_seat(self, number, Train, is_valid=True):
        try:
            return TrainSeat.objects.filter(number=number, Train=Train, is_valid=is_valid).get()
        except TrainSeat.DoesNotExist:
            raise exceptions.ValidationError(
                "Seat Dose not exist for this Airport: {} with Train number: {}!".format(
                    Train.source.title, Train.transport_number))


# ---------------------------------------------Train-----------------------------------------------------------------


class ListTrainAPIView(generics.ListAPIView):
    queryset = Train.objects.filter(
        transport_status=TransportStatus.SPACE, transfer_date__gt=timezone.now(), is_valid=True).all()
    serializer_class = TrainSerializer
    permission_classes = [AllowAny]
    filter_backends = (filters.SearchFilter,)
    search_fields = ['transport_status', 'transfer_date']

    def get_queryset(self):
        source = self.request.query_params.get('source', None)
        destination = self.request.query_params.get('destination', None)
        count = self.request.query_params.get('count', None)
        query = super(ListTrainAPIView, self).get_queryset()

        if source and destination:
            source_country = Train.objects.filter(address__city__icontains=source).all()
            destination_country = Train.objects.filter(address__city__icontains=destination).all()
            query = query.filter(source_id__in=source_country, destination_id__in=destination_country)
        if count:
            query = query.annotate(reserv=models.F('max_reservation') - models.F('number_reserved')) \
                .filter(reserv__gte=count)

        if not query:
            raise exceptions.ValidationError("Not found any Train with this searching!")
        return query


class DetailTrainAPIView(generics.RetrieveAPIView):
    queryset = Train.objects.filter(
        transport_status=TransportStatus.SPACE, transfer_date__gt=timezone.now(), is_valid=True).all()
    serializer_class = TrainSerializer
    permission_classes = [AllowAny]


# ---------------------------------------------TrainSeat-------------------------------------------------------------

class ListTrainSeatAPIView(TrainMixin, generics.ListAPIView):
    authentication_classes = []
    serializer_class = TrainSeatSerializer
    permission_classes = [AllowAny]
    filter_backends = (filters.SearchFilter,)
    search_fields = ['Train__transport_status', 'status', 'transfer_date']

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        Train = self.get_Train(pk)
        return TrainSeat.objects.filter(
            Train=Train, is_valid=True).all()


# ---------------------------------------------TrainReservation------------------------------------------------------
class CreateTrainReservationAPIView(TrainMixin, generics.CreateAPIView):
    serializer_class = TrainReservationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk', None)
        Train = self.get_Train(pk)

        request.data['Train'] = Train.id
        request.data['user'] = request.user.id
        return super(CreateTrainReservationAPIView, self).create(request, *args, **kwargs)


class DetailTrainReservationAPIView(TrainMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = TrainReservation.objects.filter(reserved_status__in=[ReservedStatus.INITIAL, ReservedStatus.RESERVED],
                                                  is_valid=True).all()
    serializer_class = TrainReservationSerializer
    permission_classes = [IsOwner]
    lookup_field = 'reserved_key'

    def update(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        try:
            request.data['Train'] = self.get_object().Train_id
        except Exception as e:
            raise exceptions.ValidationError(
                "Reservation record not found for this reserved key: {}".format(self.kwargs['reserved_key']))
        return super(DetailTrainReservationAPIView, self).update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        cancel_Train_reservation(instance)


# ---------------------------------------------PaymentReservation-------------------------------------------------------


class PaymentReservationAPIView(TrainMixin, generics.CreateAPIView):
    permission_classes = [IsOwner]
    lookup_field = 'reserved_key'

    def post(self, request, *args, **kwargs):
        data = update_reservation(request, **kwargs)
        return response.Response(data=data, status=status.HTTP_200_OK)




# Create your views here.

