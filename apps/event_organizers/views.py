from decimal import Decimal

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated)
from rest_framework.response import Response

from tourism_ecosystem.permissions import IsAdminOrReadOnly
from tourism_ecosystem.responses import CustomResponse
from .models import (Event, VenueBooking, EventPromotion)
from .serializers import (EventSerializer, VenueBookingSerializer,
                          EventPromotionSerializer, CalculatePriceSerializer)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrReadOnly]  # 只有管理员可以访问


class VenueBookingViewSet(viewsets.ModelViewSet):
    queryset = VenueBooking.objects.all()
    serializer_class = VenueBookingSerializer

    @action(detail=False,
            methods=['post'],
            url_path='calculate-price',
            permission_classes=[IsAuthenticated],
            serializer_class=CalculatePriceSerializer)
    def calculate_price(self, request, *args, **kwargs):
        """
        计算并返回总金额，只需要事件和票数作为参数
        """
        # 使用自定义的序列化器进行数据验证
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 从序列化器中获取经过验证的参数
        event_id = serializer.validated_data.get('event')
        number_of_tickets = serializer.validated_data.get('number_of_tickets')
        discount = 1  # 默认折扣为1
        discount_amount = 0
        try:
            # 获取事件对象
            event = Event.objects.get(id=event_id)
            # 使用 Decimal 进行金额计算
            ticket_price = Decimal(event.entry_fee)
            # 确保所有金额计算使用 Decimal
            base_amount = ticket_price * Decimal(number_of_tickets)

            # 检查是否有促销活动
            promotion = EventPromotion.objects.filter(
                event=event,
                promotion_start_date__lte=timezone.now().date(),
                promotion_end_date__gte=timezone.now().date()
            ).order_by('-discount').first()

            if promotion:
                discount = Decimal(promotion.discount)

                # 判断折扣是小数还是百分数
                if discount <= 1:
                    # 如果折扣小于1，直接作为小数使用
                    discount_amount = base_amount * (1 - discount)
                else:
                    # 超过1的折扣抛出错误
                    return Response(
                        {"detail": "Discount value cannot be greater than 1."},
                        status=status.HTTP_400_BAD_REQUEST)

                total_amount = base_amount - discount_amount
            else:
                total_amount = base_amount

                # 返回计算后的总金额
            return Response(
                {"event": event_id,
                 "ticket_price": ticket_price,
                 "number_of_tickets": number_of_tickets,
                 "discount": discount,
                 "base_amount": base_amount,
                 "total_amount": total_amount,
                 "discount_amount": discount_amount
                 }, status=status.HTTP_200_OK)

        except Event.DoesNotExist:
            return CustomResponse.error(
                "Event not found.",
                status.HTTP_404_NOT_FOUND
            )


class EventPromotionViewSet(viewsets.ModelViewSet):
    queryset = EventPromotion.objects.all()
    serializer_class = EventPromotionSerializer
    permission_classes = [IsAdminOrReadOnly]  # 只有管理员可以访问
