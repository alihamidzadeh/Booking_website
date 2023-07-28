from django.contrib import admin
from hotel.models import *


# Register your models here.
class HotelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'residence_status'
                    , 'star', 'room_count', 'is_valid')
    search_fields = ('name', 'star', 'residence_status')
    list_filter = ('is_valid', 'residence_status', 'star')


class HotelRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'capacity', 'status', 'price', 'hotel')
    search_fields = ('id', 'hotel')
    list_filter = ('status', 'capacity')


class HotelRatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'rate', 'hotel', 'is_valid')
    search_fields = ('hotel',)
    list_filter = ('user', 'rate', 'hotel')

    def save_model(self, request, obj, form, change):
        if change and not obj.validated_by and 'status' in form.changed_data:
            obj.validated_by = request.user

        obj.save()


class HotelPassengerAdmin(admin.ModelAdmin):
    list_display = ('id', 'national_id', 'room', 'stay_status', 'reserved_key', 'parent')
    search_fields = ('national_id', 'reserved_key')
    list_filter = ('stay_status', 'room')


class HotelReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'room', 'check_in_date', 'check_out_date', 'reserved_key',)
    search_fields = ('reserved_key', 'room')
    list_filter = ('room', 'reserved_status')


class HotelAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'country', 'city', 'address', 'phone')
    search_fields = ('country', 'city')
    list_filter = ('country', 'city')


admin.site.register(Hotel, HotelAdmin)
admin.site.register(HotelRoom, HotelRoomAdmin)
admin.site.register(HotelRating, HotelRatingAdmin)
admin.site.register(HotelPassenger, HotelPassengerAdmin)
admin.site.register(HotelReservation, HotelReservationAdmin)
admin.site.register(HotelAddress, HotelAddressAdmin)
