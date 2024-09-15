from django.contrib import admin

from .models import Room, Guest, Booking


# Register your models here.

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number',
                    'room_type',
                    'price_per_night',
                    'is_available'
                    )
    search_fields = ('room_number', 'room_type')


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number')
    search_fields = ('first_name', 'last_name', 'email')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('guest', 'room', 'check_in', 'check_out', 'total_price')
    search_fields = ('guest__first_name', 'guest__last_name',
                     'room__room_number')
    list_filter = ('check_in', 'check_out')
