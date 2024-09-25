# Register your models here.
from django.contrib import admin
from .models import Destination, Tour, EventNotification


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'location', 'opening_hours', 'contact_info')
    search_fields = ('name', 'category', 'location')
    list_filter = ('category',)


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'tour_type', 'duration', 'price_per_person', 'max_capacity', 'tour_date', 'guide_name')
    search_fields = ('name', 'destination__name', 'guide_name')
    list_filter = ('tour_type', 'tour_date', 'max_capacity')


@admin.register(EventNotification)
class EventNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'location', 'entry_fee', 'target_audience')
    search_fields = ('title', 'location', 'target_audience')
    list_filter = ('event_date', 'target_audience')
