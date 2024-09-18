# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from apps.restaurants_cafes.models import Restaurant, TableReservation, Menu, OnlineOrder
from apps.restaurants_cafes.serializers import RestaurantSerializer
from tourism_ecosystem.permissions import IsAdminOrReadOnly


@extend_schema(tags=['RC - Restaurant'])
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAdminOrReadOnly]

@extend_schema(tags=['RC - TableReservation'])
class TableReservationViewSet(viewsets.ModelViewSet):
    queryset = TableReservation.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAdminOrReadOnly]

@extend_schema(tags=['RC - Menu'])
class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAdminOrReadOnly]

@extend_schema(tags=['RC - OnlineOrder'])
class OnlineOrderViewSet(viewsets.ModelViewSet):
    queryset = OnlineOrder.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAdminOrReadOnly]