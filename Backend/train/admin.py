from django.contrib import admin
from django.contrib import admin
from django.contrib import admin

from train.models import *


class TrainAdmin(admin.ModelAdmin):
    list_display = ('id', 'transport_status'
                    , 'transport_number', 'max_reservation', 'number_reserved')
    search_fields = ('Train__source__title','transport_number')
    list_filter = ('transport_status',)


class TrainSeatAdmin(admin.ModelAdmin):
    list_display = ('id', 'Train', 'number', 'status', 'price',)
    search_fields = ('number',)
    list_filter = ('status',)



class TrainPassengerAdmin(admin.ModelAdmin):
    list_display = ('id', 'national_id', 'seat', 'transfer_status', 'reserved_key', 'parent')
    search_fields = ('national_id', 'reserved_key', 'seat__number',
                     'seat__Train__source__title')
    list_filter = ('transfer_status',)


class TrainReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'Train', 'reserved_key',)
    search_fields = ('reserved_key',)
    list_filter = ('Train__source__title',
                   'reserved_status')


class TrainAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'address', 'phone')
    search_fields = ('address','phone')
    list_filter = ('address','phone')

class RailwayAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'address',)
    search_fields = ('title','address',)
    list_filter = ('title',)


admin.site.register(Train, TrainAdmin)
admin.site.register(TrainSeat, TrainSeatAdmin)
admin.site.register(TrainPassenger, TrainPassengerAdmin)
admin.site.register(TrainReservation, TrainReservationAdmin)
admin.site.register(railwayAddress, TrainAddressAdmin)
admin.site.register(Railway_station, RailwayAdmin)



