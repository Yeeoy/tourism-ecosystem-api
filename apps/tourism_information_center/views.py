# Create your views here.
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated

from apps.tourism_information_center.models import Destination, Tour, EventNotification, TourBooking
from apps.tourism_information_center.serializers import DestinationSerializer, TourSerializer, \
    EventNotificationSerializer, TourBookingSerializer
from tourism_ecosystem.permissions import IsAdminOrReadOnly
from tourism_ecosystem.views import LoggingViewSet


@extend_schema(tags=['TIC - Destination'])
class DestinationViewSet(LoggingViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [IsAdminOrReadOnly]
    activity_name = "Destination"  # 确保这里设置了正确的activity_name


@extend_schema(tags=['TIC - Tour'])
class TourViewSet(LoggingViewSet):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = [IsAdminOrReadOnly]
    activity_name = "Tour"


@extend_schema(tags=['TIC - Event Notification'])
class EventNotificationViewSet(LoggingViewSet):
    queryset = EventNotification.objects.all()
    serializer_class = EventNotificationSerializer
    permission_classes = [IsAdminOrReadOnly]
    activity_name = "Event Notification"


@extend_schema(tags=['TIC - Tour Booking'])
class TourBookingViewSet(LoggingViewSet):
    queryset = TourBooking.objects.all()
    serializer_class = TourBookingSerializer
    permission_classes = [IsAuthenticated]
    activity_name = "Tour Booking"

    def perform_create(self, serializer):
        # Automatically set the current logged-in user as user_id
        serializer.save(user_id=self.request.user)

    def get_queryset(self):
        user = self.request.user
        # If the user is an admin, return all bookings
        if user.is_staff or user.is_superuser:
            return TourBooking.objects.all()
        # If the user is a regular user, return only the bookings related to the current user
        return TourBooking.objects.filter(user_id=user)
