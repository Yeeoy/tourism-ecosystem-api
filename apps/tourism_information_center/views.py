# Create your views here.
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from apps.tourism_information_center.models import Destination, Tour, EventNotification
from apps.tourism_information_center.serializers import DestinationSerializer, TourSerializer, \
    EventNotificationSerializer
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
