from django.contrib import admin

from .models import Event, VenueBooking, EventPromotion


# 注册 Event 模型
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'venue', 'event_date', 'start_time', 'end_time', 'entry_fee', 'max_participants')
    search_fields = ('name', 'venue', 'description')
    list_filter = ('event_date', 'venue')
    ordering = ('event_date',)
    date_hierarchy = 'event_date'


# 注册 VenueBooking 模型
@admin.register(VenueBooking)
class VenueBookingAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'booking_date', 'number_of_tickets', 'total_amount', 'booking_status', 'promotion_id')
    search_fields = ('event_id__name', 'event_id__venue')
    list_filter = ('booking_status', 'event_id__event_date', 'promotion_id')
    ordering = ('-booking_date',)
    date_hierarchy = 'booking_date'


# 注册 EventPromotion 模型
@admin.register(EventPromotion)
class EventPromotionAdmin(admin.ModelAdmin):
    list_display = ('event', 'promotion_start_date', 'promotion_end_date', 'discount')
    search_fields = ('event__name',)
    list_filter = ('promotion_start_date', 'promotion_end_date', 'event__name')
    ordering = ('-promotion_start_date',)
