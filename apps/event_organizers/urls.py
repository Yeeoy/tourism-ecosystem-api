from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import EventViewSet, VenueBookingViewSet, EventPromotionViewSet

router = DefaultRouter()
router.register('event', EventViewSet,
                basename='event')
router.register('venue-booking', VenueBookingViewSet,
                basename='venue-booking')
router.register('event-promotion', EventPromotionViewSet,
                basename='event-promotion')

app_name = 'event_organizers'

urlpatterns = [
    path('', include(router.urls)),
]
