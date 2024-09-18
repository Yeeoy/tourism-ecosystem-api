# Create your views here.
from rest_framework import viewsets

from apps.local_transportation_services.models import TransportationProvider, RideBooking, RoutePlanning, TrafficUpdate
from apps.local_transportation_services.serializers import TransportationServiceSerializer, RideBookingSerializer, \
    RoutePlanningSerializer, TrafficUpdateSerializer
from tourism_ecosystem.permissions import IsAdminOrReadOnly, IsOwnerOrAdmin


class TransportationProviderViewSet(viewsets.ModelViewSet):
    queryset = TransportationProvider.objects.all()
    serializer_class = TransportationServiceSerializer
    permission_classes = [IsAdminOrReadOnly]


class RideBookingViewSet(viewsets.ModelViewSet):
    queryset = RideBooking.objects.all()
    serializer_class = RideBookingSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        # 如果是管理员用户，返回所有订单
        if user.is_staff or user.is_superuser:
            return RideBooking.objects.all()
        # 如果是普通用户，只返回与当前用户相关的订单
        return RideBooking.objects.filter(user_id=user)


class RoutePlanningViewSet(viewsets.ModelViewSet):
    queryset = RoutePlanning.objects.all()
    serializer_class = RoutePlanningSerializer
    permission_classes = [IsAdminOrReadOnly]


class TrafficUpdateViewSet(viewsets.ModelViewSet):
    queryset = TrafficUpdate.objects.all()
    serializer_class = TrafficUpdateSerializer
    permission_classes = [IsAdminOrReadOnly]
