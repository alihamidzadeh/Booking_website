from django.shortcuts import render
from rest_framework import generics, response, status, filters
from rest_framework.permissions import IsAdminUser, AllowAny, SAFE_METHODS, IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework_simplejwt.authentication import JWTAuthentication

from airplane.serializers import *
from user.permissions import IsOwner


class AirplaneMixin:
    authentication_classes = [JWTAuthentication]
    throttle_classes = [UserRateThrottle]

    def get_airplane(self, pk, is_valid=True):
        try:
            return Airplane.objects.filter(
                pk=pk, transport_status=TransportStatus.SPACE,
                is_valid=is_valid).get()
        except Airplane.DoesNotExist:
            raise exceptions.ValidationError("Airplane Dose not exist fot this id: {}!".format(pk))

    def get_company(self, name, is_valid=True):
        try:
            return AirplaneCompany.objects.filter(name__iexact=name, is_valid=is_valid).get()
        except AirplaneCompany.DoesNotExist:
            raise exceptions.ValidationError("Airplane company Dose not exist with this name in url!")

    def get_reservation(self, reserved_key, is_valid):
        try:
            if is_valid:
                return AirplaneReservation.objects.filter(reserved_key=reserved_key, is_valid=is_valid).get()
            return AirplaneReservation.objects.filter(reserved_key=reserved_key).get()
        except AirplaneReservation.DoesNotExist:
            raise exceptions.ValidationError("This reserved Dose not exist with this key: {}!".format(reserved_key))

    def get_seat(self, number, airplane, is_valid=True):
        try:
            return AirplaneSeat.objects.filter(number=number, airplane=airplane, is_valid=is_valid).get()
        except AirplaneSeat.DoesNotExist:
            raise exceptions.ValidationError(
                "Seat Dose not exist for this Airport: {} with Airplane number: {}!".format(
                    airplane.company.name, airplane.transport_number))


# ---------------------------------------------Airplane-----------------------------------------------------------------


class ListAirplaneAPIView(generics.ListAPIView):
    queryset = Airplane.objects.filter(
    transport_status=TransportStatus.SPACE, is_valid=True).all()
    serializer_class = AirplaneSerializer
    permission_classes = [AllowAny]
    filter_backends = (filters.SearchFilter,)
    search_fields = ['transport_status', 'transfer_date']

    def get_queryset(self):
        source = self.request.query_params.get('source', None)
        destination = self.request.query_params.get('destination', None)
        count = self.request.query_params.get('count', None)
        query = super(ListAirplaneAPIView, self).get_queryset()

        # if source and destination:
        #     query = query.filter(source_id__in=source, destination_id__in=destination)
        # if count:
        #     query = query.annotate(reserv=models.F('max_reservation') - models.F('number_reserved')) \
        #         .filter(reserv__gte=count)

        # if not query:
        #     raise exceptions.ValidationError("Not found any airplane with this searching!")
        return query


class DetailAirplaneAPIView(generics.RetrieveAPIView):
    queryset = Airplane.objects.filter(
        transport_status=TransportStatus.SPACE, transfer_date__gt=timezone.now(), is_valid=True).all()
    serializer_class = AirplaneSerializer
    permission_classes = [AllowAny]


# ---------------------------------------------AirplaneSeat-------------------------------------------------------------

class ListAirplaneSeatAPIView(AirplaneMixin, generics.ListAPIView):
    authentication_classes = []
    serializer_class = AirplaneSeatSerializer
    permission_classes = [AllowAny]
    filter_backends = (filters.SearchFilter,)
    search_fields = ['airplane__transport_status', 'status', 'transfer_date']

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        airplane = self.get_airplane(pk)
        return AirplaneSeat.objects.filter(
            airplane=airplane, is_valid=True).all()


# ---------------------------------------------AirplaneReservation------------------------------------------------------
class CreateAirplaneReservationAPIView(AirplaneMixin, generics.CreateAPIView):
    serializer_class = AirplaneReservationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk', None)
        airplane = self.get_airplane(pk)

        request.data['airplane'] = airplane.id
        request.data['user'] = request.user.id
        return super(CreateAirplaneReservationAPIView, self).create(request, *args, **kwargs)


class DetailAirplaneReservationAPIView(AirplaneMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = AirplaneReservation.objects.filter(reserved_status__in=[ReservedStatus.INITIAL, ReservedStatus.RESERVED],
                                                  is_valid=True).all()
    serializer_class = AirplaneReservationSerializer
    permission_classes = [IsOwner]
    lookup_field = 'reserved_key'

    def update(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        try:
            request.data['airplane'] = self.get_object().airplane_id
        except Exception as e:
            raise exceptions.ValidationError(
                "Reservation record not found for this reserved key: {}".format(self.kwargs['reserved_key']))
        return super(DetailAirplaneReservationAPIView, self).update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        cancel_airplane_reservation(instance)


# ---------------------------------------------PaymentReservation-------------------------------------------------------


class PaymentReservationAPIView(AirplaneMixin, generics.CreateAPIView):
    permission_classes = [IsOwner]
    lookup_field = 'reserved_key'

    def post(self, request, *args, **kwargs):
        data = update_reservation(request, **kwargs)
        return response.Response(data=data, status=status.HTTP_200_OK)


# ---------------------------------------------AirplaneCompanyRate------------------------------------------------------

class CreateAirplaneCompanyRateAPIView(AirplaneMixin, generics.CreateAPIView):
    serializer_class = AirplaneCompanyRatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        name = self.kwargs.get('name', None)
        return self.get_company(name)

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        request.data['company'] = self.get_queryset().id
        return super(CreateAirplaneCompanyRateAPIView, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        try:
            super(CreateAirplaneCompanyRateAPIView, self).perform_create(serializer)
        except IntegrityError:
            raise exceptions.ValidationError(
                "Error: This user: {} has rated to company: {}".format(self.request.user, self.get_queryset().name))


class DetailAirplaneCompanyRateAPIView(AirplaneMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AirplaneCompanyRatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        name = self.kwargs.get('name', None)
        company = self.get_company(name)

        if self.request.method in SAFE_METHODS:
            return AirplaneCompanyRating.objects.filter(company=company, is_valid=True).all()

        return AirplaneCompanyRating.objects.filter(company=company).all()

    def update(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        request.data['company'] = self.get_queryset().first().company_id

        return super(DetailAirplaneCompanyRateAPIView, self).update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.is_valid = False
        instance.save()


# Create your views here.
