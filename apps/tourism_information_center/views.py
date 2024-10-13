# Create your views here.
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.tourism_information_center.models import Destination, Tour, EventNotification, TourBooking
from apps.tourism_information_center.serializers import DestinationSerializer, TourSerializer, \
    EventNotificationSerializer, TourBookingSerializer
from tourism_ecosystem.permissions import IsAdminOrReadOnly


@extend_schema(tags=['TIC - Destination'])
class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [IsAdminOrReadOnly]
    log_event = True
    activity_name = "Destination Management"


@extend_schema(tags=['TIC - Tour'])
class TourViewSet(viewsets.ModelViewSet):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = [IsAdminOrReadOnly]
    log_event = True
    activity_name = "Tour Management"


@extend_schema(tags=['TIC - Event Notification'])
class EventNotificationViewSet(viewsets.ModelViewSet):
    queryset = EventNotification.objects.all()
    serializer_class = EventNotificationSerializer
    permission_classes = [IsAdminOrReadOnly]
    log_event = True
    activity_name = "Event Notification Management"


@extend_schema(tags=['TIC - Tour Booking'])
class TourBookingViewSet(viewsets.ModelViewSet):
    queryset = TourBooking.objects.all()
    serializer_class = TourBookingSerializer
    permission_classes = [IsAuthenticated]
    log_event = True
    activity_name = "Tour Booking Management"

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
