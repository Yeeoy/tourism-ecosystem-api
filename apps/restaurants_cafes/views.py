# Create your views here.
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from apps.restaurants_cafes.models import Restaurant, TableReservation, Menu, OnlineOrder
from apps.restaurants_cafes.serializers import RestaurantSerializer, OnlineOrderSerializer, MenuSerializer, \
    TableReservationSerializer
from tourism_ecosystem.permissions import IsAdminOrReadOnly, IsOwnerOrAdmin


@extend_schema(tags=['RC - Restaurant'])
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema(tags=['RC - TableReservation'])
class TableReservationViewSet(viewsets.ModelViewSet):
    queryset = TableReservation.objects.all()
    serializer_class = TableReservationSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        # 如果是管理员用户，返回所有订单
        if user.is_staff or user.is_superuser:
            return TableReservation.objects.all()
        # 如果是普通用户，只返回与当前用户相关的订单
        return TableReservation.objects.filter(user_id=user)


@extend_schema(tags=['RC - Menu'])
class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema(tags=['RC - OnlineOrder'])
class OnlineOrderViewSet(viewsets.ModelViewSet):
    queryset = OnlineOrder.objects.all()
    serializer_class = OnlineOrderSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        # If admin user, return all orders
        if user.is_staff or user.is_superuser:
            return OnlineOrder.objects.all()
        # In case of a regular user, only orders related to the current user are returned
        return OnlineOrder.objects.filter(user_id=user)
