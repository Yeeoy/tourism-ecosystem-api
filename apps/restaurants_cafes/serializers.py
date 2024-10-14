from decimal import Decimal
from rest_framework import serializers
from apps.restaurants_cafes.models import Restaurant, TableReservation, Menu, OnlineOrder, OrderItem


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'
        read_only_fields = ['id', ]


class TableReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableReservation
        fields = '__all__'
        read_only_fields = ['id', ]


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'
        read_only_fields = ['id', ]


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = MenuSerializer(read_only=True)
    menu_item_id = serializers.PrimaryKeyRelatedField(
        queryset=Menu.objects.all(), source='menu_item', write_only=True
    )
    subtotal = serializers.SerializerMethodField()  # 添加subtotal计算方法

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_id', 'quantity', 'subtotal']
        read_only_fields = ['id', 'subtotal']

    def get_subtotal(self, obj):
        return obj.subtotal()  # 调用模型中的subtotal方法


class OnlineOrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = OnlineOrder
        fields = '__all__'
        read_only_fields = ['id', 'total_amount']

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')

        # 创建订单对象
        order = OnlineOrder.objects.create(
            user=validated_data.get('user'),
            restaurant=validated_data.get('restaurant'),
            order_date=validated_data.get('order_date'),
            order_time=validated_data.get('order_time'),
            order_status=validated_data.get('order_status'),
            total_amount=Decimal(0)  # 初始设置为0，稍后会更新
        )

        # 计算总金额并创建订单项
        order_items = []
        total_amount = Decimal(0)
        for item_data in order_items_data:
            menu_item = item_data['menu_item']
            quantity = item_data['quantity']
            item = OrderItem(
                order=order,
                menu_item=menu_item,
                quantity=quantity
            )
            total_amount += menu_item.price * quantity  # 直接计算小计
            order_items.append(item)

        # 批量创建订单项，减少数据库交互
        OrderItem.objects.bulk_create(order_items)

        # 更新订单的 total_amount 字段
        order.total_amount = total_amount
        order.save()

        return order

    def update(self, instance, validated_data):
        order_items_data = validated_data.pop('order_items', None)

        # 更新订单的基本字段
        instance.order_status = validated_data.get('order_status', instance.order_status)
        instance.save()

        # 如果提供了订单项，则处理它们
        if order_items_data:
            # 删除现有的订单项
            instance.order_items.all().delete()
            # 重新创建新的订单项
            order_items = []
            total_amount = Decimal(0)
            for item_data in order_items_data:
                menu_item = item_data['menu_item']
                quantity = item_data['quantity']
                item = OrderItem(
                    order=instance,
                    menu_item=menu_item,
                    quantity=quantity
                )
                total_amount += menu_item.price * quantity
                order_items.append(item)

            # 批量创建订单项
            OrderItem.objects.bulk_create(order_items)

            # 更新订单的总金额
            instance.total_amount = total_amount
            instance.save()

        return instance


class ItemSerializer(serializers.Serializer):
    menu_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class CalculateOrderSerializer(serializers.Serializer):
    items = ItemSerializer(many=True)

    def validate(self, data):
        """
        验证所有提供的菜单项在数据库中存在。
        """
        items = data.get('items', [])
        menu_item_ids = [item['menu_item_id'] for item in items]
        existing_items = Menu.objects.filter(id__in=menu_item_ids)
        existing_ids = set(existing_items.values_list('id', flat=True))
        missing_ids = set(menu_item_ids) - existing_ids

        if missing_ids:
            raise serializers.ValidationError(f"菜单项 ID {missing_ids} 不存在。")

        return data

    def calculate_total(self):
        total = Decimal(0)
        for item in self.validated_data['items']:
            menu_item = Menu.objects.get(id=item['menu_item_id'])
            quantity = item['quantity']
            total += menu_item.price * quantity
        return total
