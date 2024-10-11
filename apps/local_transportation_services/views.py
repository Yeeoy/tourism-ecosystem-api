# Create your views here.
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from apps.local_transportation_services.models import TransportationProvider, RideBooking, RoutePlanning, TrafficUpdate
from apps.local_transportation_services.serializers import TransportationServiceSerializer, RideBookingSerializer, \
    RoutePlanningSerializer, TrafficUpdateSerializer
from tourism_ecosystem.permissions import IsAdminOrReadOnly, IsOwnerOrAdmin


@extend_schema(tags=['LTS - Transportation Provider'])
class TransportationProviderViewSet(viewsets.ModelViewSet):
    queryset = TransportationProvider.objects.all()
    serializer_class = TransportationServiceSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema(tags=['LTS - Ride Booking'])
class RideBookingViewSet(viewsets.ModelViewSet):
    queryset = RideBooking.objects.all()
    serializer_class = RideBookingSerializer
    permission_classes = [IsOwnerOrAdmin]
    log_event = True
    activity_name = "Ride Booking Management"

    def get_queryset(self):
        user = self.request.user
        # If admin user, return all orders
        if user.is_staff or user.is_superuser:
            return RideBooking.objects.all()
        # In case of a regular user, only orders related to the current user are returned
        return RideBooking.objects.filter(user_id=user)


@extend_schema(tags=['LTS - Route Planning'])
class RoutePlanningViewSet(viewsets.ModelViewSet):
    queryset = RoutePlanning.objects.all()
    serializer_class = RoutePlanningSerializer
    permission_classes = [IsAdminOrReadOnly]
    log_event = True
    activity_name = "Route Planning Management"


@extend_schema(tags=['LTS - Traffic Update'])
class TrafficUpdateViewSet(viewsets.ModelViewSet):
    queryset = TrafficUpdate.objects.all()
    serializer_class = TrafficUpdateSerializer
    permission_classes = [IsAdminOrReadOnly]
    log_event = True
    activity_name = "Traffic Update Management"
