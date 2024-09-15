from django.contrib import admin

from .models import (Museum, Ticket,
                     TourGuide, Booking, EducationContent)


# Register your models here.
# Local Attractions and Museums
# Attraction 模型的自定义管理类
class AttractionAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'opening_hours')
    search_fields = ('name', 'location')
    list_filter = ('location',)


# Museum 模型的自定义管理类
class MuseumAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name', 'location')
    list_filter = ('location',)


# Ticket 模型的自定义管理类
class TicketAdmin(admin.ModelAdmin):
    list_display = ('attraction', 'museum', 'price',
                    'purchase_date', 'valid_until')
    search_fields = ('attraction__name', 'museum__name')
    list_filter = ('purchase_date', 'valid_until')


# TourGuide 模型的自定义管理类
class TourGuideAdmin(admin.ModelAdmin):
    list_display = ('name', 'available_from',
                    'available_to', 'languages')
    search_fields = ('name', 'languages')
    list_filter = ('languages',)


# Booking 模型的自定义管理类
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'ticket', 'guide',
                    'booking_date', 'visit_date')
    search_fields = ('user__username',
                     'ticket__attraction__name', 'guide__name')
    list_filter = ('booking_date', 'visit_date')


# EducationContent 模型的自定义管理类
class EducationContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'related_museum',
                    'related_attraction')
    search_fields = ('title', 'related_museum__name',
                     'related_attraction__name')
    list_filter = ('related_museum',
                   'related_attraction')


admin.site.register(Museum, MuseumAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(TourGuide, TourGuideAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(EducationContent, EducationContentAdmin)
