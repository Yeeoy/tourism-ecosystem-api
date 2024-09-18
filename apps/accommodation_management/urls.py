from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (AccommodationViewSet, RoomTypeViewSet, RoomBookingViewSet, GuestServiceViewSet,
                    FeedbackReviewViewSet)

router = DefaultRouter()
router.register('accommodation', AccommodationViewSet)
router.register('room-type', RoomTypeViewSet, basename='room-type')
router.register('room-booking', RoomBookingViewSet, basename='room-booking')
router.register('guest-service', GuestServiceViewSet, basename='guest-service')
router.register('feedback-review', FeedbackReviewViewSet, basename='feedback-review')

app_name = 'accommodation_management'

urlpatterns = [
    path('', include(router.urls)),
]
