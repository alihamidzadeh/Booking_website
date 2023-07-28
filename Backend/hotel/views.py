from rest_framework import generics, response, status, filters
from rest_framework.permissions import IsAdminUser, AllowAny, SAFE_METHODS, IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework_simplejwt.authentication import JWTAuthentication

from hotel.serializers import *
from reservation.base_models.reservation import ReservedStatus
from reservation.models import Payment, PaymentStatus
from user.permissions import IsOwner


class HotelMixin:
    authentication_classes = [JWTAuthentication]
    throttle_classes = [UserRateThrottle]

    def get_hotel(self, name, is_valid=True):
        try:
            return Hotel.objects.filter(name__iexact=name, is_valid=is_valid).get()
        except Hotel.DoesNotExist:
            raise exceptions.ValidationError("Hotel Dose not exist with this name in url!")

    def get_room(self, number, hotel, is_valid=True):
        try:
            room = HotelRoom.objects.filter(number=number, hotel=hotel, is_valid=is_valid).get()
            if room.status != RoomStatus.FREE:
                raise exceptions.ValidationError("This room not free yet in this hotel: {}!".format(hotel.name))
            return room
        except HotelRoom.DoesNotExist:
            raise exceptions.ValidationError("room Dose not exist for this hotel: {}!".format(hotel.name))

# ---------------------------------------------Hotel-------------------------------------------------------------------


class ListCreateHotelAPIView(HotelMixin, generics.ListCreateAPIView):
    queryset = Hotel.objects.filter(is_valid=True).all()
    serializer_class = HotelSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['star', 'name', 'residence_status']

    def get_queryset(self):
        # city = self.request.query_params.get('city', None)
        # country = self.request.query_params.get('country', None)
        query = super(ListCreateHotelAPIView, self).get_queryset()

        # if city or country:
        #     if country:
        #         query = query.filter(address__country__icontains=country)
        #     if city:
        #         query = query.filter(address__city__icontains=city)
        # if not query:
        #     raise exceptions.ValidationError("Not found any hotel with this searching!")
        return query

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        else:
            return [IsAdminUser()]


class DetailHotelAPIView(HotelMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

    def get_queryset(self):
        if self.request.method in SAFE_METHODS:
            return Hotel.objects.filter(is_valid=True).all()
        else:
            return Hotel.objects.all()

    def get_object(self):
        name = self.kwargs.get('name', None)
        obj = self.get_hotel(name)

        self.check_object_permissions(self.request, obj)
        return obj

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        else:
            return [IsAdminUser()]

    def perform_destroy(self, instance):
        instance.is_valid = False
        instance.save()


# ---------------------------------------------HotelRoom----------------------------------------------------------------

class ListCreateHotelRoomAPIView(HotelMixin, generics.ListCreateAPIView):
    queryset = HotelRoom.objects.filter(is_valid=True).all().select_related('hotel')
    serializer_class = HotelRoomSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['capacity', 'status', ]

    def get_queryset(self):
        name = self.kwargs.get('name', None)
        hotel = self.get_hotel(name)

        return HotelRoom.objects.filter(hotel=hotel, is_valid=True).all().select_related('hotel')

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        else:
            return [IsAdminUser()]

    def create(self, request, *args, **kwargs):
        request.data['hotel'] = self.get_queryset().first().hotel_id
        return super(ListCreateHotelRoomAPIView, self).create(request, *args, **kwargs)


class DetailHotelRoomAPIView(HotelMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = HotelRoom.objects.filter(is_valid=True).all().select_related('hotel')
    serializer_class = HotelRoomSerializer
    lookup_field = 'number'

    def get_queryset(self):
        name = self.kwargs.get('name', None)
        hotel = self.get_hotel(name)

        if self.request.method in SAFE_METHODS:
            return HotelRoom.objects.filter(hotel=hotel, is_valid=True).all().select_related('hotel')
        else:
            return HotelRoom.objects.filter(hotel=hotel).all().select_related('hotel')

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        else:
            return [IsAdminUser()]

    def update(self, request, *args, **kwargs):
        request.data['hotel'] = self.get_queryset().first().hotel_id
        return super(DetailHotelRoomAPIView, self).update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.is_valid = False
        instance.save()


# ---------------------------------------------HotelReservation---------------------------------------------------------

class CreateHotelReservationAPIView(HotelMixin, generics.CreateAPIView):
    serializer_class = HotelReservationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        name = self.kwargs.get('name', None)
        hotel = self.get_hotel(name)

        room_number = self.kwargs.get('number', None)
        room = self.get_room(room_number, hotel)

        request.data['user'] = request.user.id
        request.data['room'] = room.id
        return super(CreateHotelReservationAPIView, self).create(request, *args, **kwargs)


class DetailHotelReservationAPIView(HotelMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = HotelReservation.objects.filter(reserved_status__in=[ReservedStatus.INITIAL, ReservedStatus.RESERVED],
                                               is_valid=True).all()
    serializer_class = HotelReservationSerializer
    permission_classes = [IsOwner]
    lookup_field = 'reserved_key'

    def update(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        try:
            request.data['room'] = self.get_object().room_id
        except Exception as e:
            raise exceptions.ValidationError(
                "Reservation record not found for this reserved key: {}".format(self.kwargs['reserved_key']))
        return super(DetailHotelReservationAPIView, self).update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        cancel_hotel_reservation(instance)


# ---------------------------------------------PaymentReservation-------------------------------------------------------


class PaymentReservationAPIView(HotelMixin, generics.CreateAPIView, generics.DestroyAPIView):
    permission_classes = [IsOwner]
    lookup_field = 'reserved_key'

    def post(self, request, *args, **kwargs):
        data = update_reservation(request, **kwargs)
        return response.Response(data=data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        instance = HotelReservation.objects.filter(reserved_key=self.kwargs['reserved_key']).get()
        instance.reserved_status = ReservedStatus.CANCELLED
        instance.save()
        Payment.objects.filter(reserved_key=instance.reserved_key).update(payment_status=PaymentStatus.CANCELLED)


# ---------------------------------------------HotelRating--------------------------------------------------------------


class CreateHotelRateAPIView(HotelMixin, generics.CreateAPIView):
    serializer_class = HotelRateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        name = self.kwargs.get('name', None)
        return self.get_hotel(name)

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        request.data['hotel'] = self.get_queryset().id
        return super(CreateHotelRateAPIView, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        try:
            super(CreateHotelRateAPIView, self).perform_create(serializer)
        except IntegrityError:
            "Error: This user: {} has rated to hotel: {}".format(self.request.user, self.get_queryset().name)


class DetailHotelRateAPIView(HotelMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HotelRateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        name = self.kwargs.get('name', None)
        hotel = self.get_hotel(name)

        if self.request.method in SAFE_METHODS:
            return HotelRating.objects.filter(hotel=hotel, is_valid=True).all()
        else:
            return HotelRating.objects.filter(hotel=hotel).all()

    def update(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        request.data['hotel'] = self.get_queryset().first().hotel_id
        return super(DetailHotelRateAPIView, self).update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.is_valid = False
        instance.save()

