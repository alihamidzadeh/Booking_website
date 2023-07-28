from django.contrib import admin
from django.contrib import admin

from airplane.models import *


class AirplaneAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'transport_status'
                    , 'transport_number', 'max_reservation', 'number_reserved')
    search_fields = ('company__name', 'transport_number')
    list_filter = ('transport_status',)

class AirplaneCompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_valid',)
    search_fields = ('is_valid',)
    list_filter = ('name',)

class AirportAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'address',)
    search_fields = ('title','address',)
    list_filter = ('title',)

class AirplaneSeatAdmin(admin.ModelAdmin):
    list_display = ('id', 'airplane', 'number', 'status', 'price',)
    search_fields = ('airplane__company__airport__title', 'number')
    list_filter = ('status',)


class AirplaneCompanyRatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'rate', 'company', 'is_valid')
    search_fields = ('company__name',)
    list_filter = ('user', 'rate',)



class AirplanePassengerAdmin(admin.ModelAdmin):
    list_display = ('id', 'national_id', 'seat', 'transfer_status', 'reserved_key', 'parent')
    search_fields = ('national_id', 'reserved_key', 'seat__number',
                     'seat__airplane__company__name')
    list_filter = ('transfer_status',)


class AirplaneReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'airplane', 'reserved_key',)
    search_fields = ('reserved_key',)
    list_filter = ('airplane__company__name',
                   'reserved_status')


class AirportAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'address', 'phone')
    search_fields = ('address','phone')
    list_filter = ('address','phone')


admin.site.register(Airplane, AirplaneAdmin)
admin.site.register(AirplaneSeat, AirplaneSeatAdmin)
admin.site.register(AirplaneCompanyRating, AirplaneCompanyRatingAdmin)
admin.site.register(AirplanePassenger, AirplanePassengerAdmin)
admin.site.register(AirplaneReservation, AirplaneReservationAdmin)
admin.site.register(AirportAddress, AirportAddressAdmin)
admin.site.register(AirplaneCompany,AirplaneCompanyAdmin)
admin.site.register(Airport, AirportAdmin)

