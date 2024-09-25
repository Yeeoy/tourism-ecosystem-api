from django.contrib import admin
from .models import Restaurant, TableReservation, Menu, OnlineOrder


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'cuisine_type', 'opening_hours', 'contact_info')
    search_fields = ('name', 'location', 'cuisine_type')
    list_filter = ('cuisine_type',)


@admin.register(TableReservation)
class TableReservationAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'user', 'reservation_date', 'reservation_time', 'number_of_guests', 'reservation_status')
    search_fields = ('restaurant__name', 'user__username')
    list_filter = ('reservation_date', 'reservation_status')


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'item_name', 'price')
    search_fields = ('item_name', 'restaurant__name')
    list_filter = ('restaurant',)


@admin.register(OnlineOrder)
class OnlineOrderAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'user', 'order_date', 'order_time', 'total_amount', 'order_status')
    search_fields = ('restaurant__name', 'user__username', 'order_status')
    list_filter = ('order_date', 'order_status')
