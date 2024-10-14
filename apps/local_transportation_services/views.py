# Create your views here.
from drf_spectacular.utils import extend_schema

from apps.local_transportation_services.models import TransportationProvider, RideBooking, RoutePlanning, TrafficUpdate
from apps.local_transportation_services.serializers import TransportationServiceSerializer, RideBookingSerializer, \
    RoutePlanningSerializer, TrafficUpdateSerializer
from tourism_ecosystem.permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from tourism_ecosystem.views import LoggingViewSet


@extend_schema(tags=['LTS - Transportation Provider'])
class TransportationProviderViewSet(LoggingViewSet):
    queryset = TransportationProvider.objects.all()
    serializer_class = TransportationServiceSerializer
    permission_classes = [IsAdminOrReadOnly]
    activity_name = "Transportation Provider"


@extend_schema(tags=['LTS - Ride Booking'])
class RideBookingViewSet(LoggingViewSet):
    queryset = RideBooking.objects.all()
    serializer_class = RideBookingSerializer
    permission_classes = [IsOwnerOrAdmin]
    activity_name = "Ride Booking"


@extend_schema(tags=['LTS - Route Planning'])
class RoutePlanningViewSet(LoggingViewSet):
    queryset = RoutePlanning.objects.all()
    serializer_class = RoutePlanningSerializer
    permission_classes = [IsAdminOrReadOnly]
    activity_name = "Route Planning"


@extend_schema(tags=['LTS - Traffic Update'])
class TrafficUpdateViewSet(LoggingViewSet):
    queryset = TrafficUpdate.objects.all()
    serializer_class = TrafficUpdateSerializer
    permission_classes = [IsAdminOrReadOnly]
    activity_name = "Traffic Update"
