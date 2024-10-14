from decimal import Decimal

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.restaurants_cafes.models import Restaurant, TableReservation, Menu, OnlineOrder
from apps.restaurants_cafes.serializers import (
    RestaurantSerializer, OnlineOrderSerializer, MenuSerializer,
    TableReservationSerializer, CalculateOrderSerializer
)
from tourism_ecosystem.permissions import IsAdminOrReadOnly
from tourism_ecosystem.views import LoggingViewSet


@extend_schema(tags=['RC - Restaurant'])
class RestaurantViewSet(LoggingViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAdminOrReadOnly]
    activity_name = "Restaurant"


@extend_schema(tags=['RC - TableReservation'])
class TableReservationViewSet(LoggingViewSet):
    queryset = TableReservation.objects.all()
    serializer_class = TableReservationSerializer
    permission_classes = [IsAuthenticated]
    activity_name = "Table Reservation"

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return TableReservation.objects.all()
        return TableReservation.objects.filter(user_id=user)


@extend_schema(tags=['RC - Menu'])
class MenuViewSet(LoggingViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsAdminOrReadOnly]
    activity_name = "Menu"

    @action(detail=False, methods=['get'],
            url_path='get_menu_by_restaurant/(?P<restaurant_id>[^/.]+)',
            permission_classes=[AllowAny])
    def get_menu_by_restaurant(self, request, restaurant_id):
        """
        Retrieve all menu items for a given restaurant by restaurant_id passed in the URL path
        """
        if not restaurant_id:
            return Response({'error': 'The restaurant_id parameter is required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Get the menu items for the specified restaurant
        menu_items = self.get_menus_by_restaurant(restaurant_id)
        serializer = self.get_serializer(menu_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_menus_by_restaurant(self, restaurant_id):
        """
        Helper method to get menu items by restaurant_id
        """
        return self.queryset.filter(restaurant_id=restaurant_id)


@extend_schema(tags=['RC - OnlineOrder'])
class OnlineOrderViewSet(LoggingViewSet):
    queryset = OnlineOrder.objects.all()
    serializer_class = OnlineOrderSerializer
    permission_classes = [IsAuthenticated]
    activity_name = "Online Order"

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return OnlineOrder.objects.all()
        return OnlineOrder.objects.filter(user_id=user)

    @action(detail=False, methods=['post'], url_path='calculate-price', permission_classes=[AllowAny],
            serializer_class=CalculateOrderSerializer)
    def calculate_price(self, request, *args, **kwargs):
        """
        Calculate and return the total price based on selected menu items and their quantities.
        """
        self.activity_name = "Calculate Order Price"
        # Use custom serializer for data validation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get validated items (list of menu_item_id and quantity)
        items = serializer.validated_data.get('items')
        menu_item_ids = [item['menu_item_id'] for item in items]

        # 获取所有相关的 Menu 对象，并检查是否存在缺失的 menu_item_id
        menu_items = Menu.objects.filter(id__in=menu_item_ids)
        existing_menu_ids = set(menu_items.values_list('id', flat=True))
        missing_menu_ids = set(menu_item_ids) - existing_menu_ids

        if missing_menu_ids:
            return Response({"detail": f"Menu items with IDs {missing_menu_ids} do not exist."},
                            status=status.HTTP_404_NOT_FOUND)

        total_price = Decimal(0)
        item_details = []

        # 迭代 items 并计算总价格
        menu_item_dict = {item.id: item for item in menu_items}
        for item in items:
            menu_item = menu_item_dict[item['menu_item_id']]
            quantity = item['quantity']
            item_price = Decimal(menu_item.price) * Decimal(quantity)
            total_price += item_price

            # Collect item details for response
            item_details.append({
                'menu_item_id': menu_item.id,
                'item_name': menu_item.item_name,
                'price_per_item': menu_item.price,
                'quantity': quantity,
                'item_price': item_price
            })

        # Return the total price and item details
        return Response({
            "items": item_details,
            "total_price": total_price
        }, status=status.HTTP_200_OK)
