from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RoomViewSet, GuestViewSet, BookingViewSet

router = DefaultRouter()
router.register('rooms', RoomViewSet)
router.register('guests', GuestViewSet)
router.register('bookings', BookingViewSet)

app_name = 'accommodation_management'

urlpatterns = [
    path('', include(router.urls)),
]
