from django.contrib import admin

from .models import Accommodation, RoomType, RoomBooking, GuestService, FeedbackReview


@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'star_rating', 'total_rooms', 'display_types')
    list_filter = ('location', 'types')
    search_fields = ('name', 'location', 'types__room_type')

    # 定义一个方法来显示多对多的房型（RoomTypes）
    def display_types(self, obj):
        return ", ".join([room_type.room_type for room_type in obj.types.all()])

    display_types.short_description = 'Room Types'


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'price_per_night', 'max_occupancy', 'availability')
    search_fields = ('room_type',)
    list_filter = ('availability', 'max_occupancy')


@admin.register(RoomBooking)
class RoomBookingAdmin(admin.ModelAdmin):
    list_display = (
        'room_type_id', 'user_id', 'check_in_date', 'check_out_date', 'total_price',
        'booking_status',
        'payment_status')
    search_fields = ('accommodation_id__name', 'room_type_id__room_type', 'user_id__username')
    list_filter = ('booking_status', 'payment_status', 'check_in_date', 'check_out_date')


@admin.register(GuestService)
class GuestServiceAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'accommodation_id', 'price', 'availability_hours')
    search_fields = ('service_name',)
    list_filter = ('accommodation_id',)


@admin.register(FeedbackReview)
class FeedbackReviewAdmin(admin.ModelAdmin):
    list_display = ('accommodation_id', 'user', 'rating', 'date')
    search_fields = ('accommodation_id__name', 'user__username')
    list_filter = ('rating', 'date')
