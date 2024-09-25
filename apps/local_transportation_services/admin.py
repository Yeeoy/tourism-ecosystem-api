from django.contrib import admin
from .models import TransportationProvider, RideBooking, RoutePlanning, TrafficUpdate


@admin.register(TransportationProvider)
class TransportationProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'base_fare', 'price_per_km', 'contact_info')
    search_fields = ('name', 'service_type')
    list_filter = ('service_type',)


@admin.register(RideBooking)
class RideBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider_id', 'pickup_location', 'drop_off_location', 'ride_date', 'pickup_time', 'estimated_fare', 'booking_status')
    search_fields = ('pickup_location', 'drop_off_location', 'user__username', 'provider_id__name')
    list_filter = ('ride_date', 'booking_status')


@admin.register(RoutePlanning)
class RoutePlanningAdmin(admin.ModelAdmin):
    list_display = ('provider_id', 'start_location', 'end_location', 'distance', 'estimated_time')
    search_fields = ('start_location', 'end_location', 'provider_id__name')
    list_filter = ('provider_id', 'distance')


@admin.register(TrafficUpdate)
class TrafficUpdateAdmin(admin.ModelAdmin):
    list_display = ('provider_id', 'update_time', 'update_message')
    search_fields = ('provider_id__name', 'update_message')
    list_filter = ('provider_id', 'update_time')
