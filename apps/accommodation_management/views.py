from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accommodation_management.models import Accommodation, RoomType, RoomBooking, GuestService, FeedbackReview
from apps.accommodation_management.serializers import AccommodationSerializer, RoomTypeSerializer, \
    RoomBookingSerializer, AccommodationCalculatePriceSerializer, GuestServiceSerializer, FeedbackReviewSerializer
from tourism_ecosystem.permissions import IsAdminOrReadOnly, IsOwnerOrAdmin


@extend_schema(tags=['AM - Accommodation'])
class AccommodationViewSet(viewsets.ModelViewSet):
    queryset = Accommodation.objects.all()
    serializer_class = AccommodationSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema(tags=['AM - Room Type'])
class RoomTypeViewSet(viewsets.ModelViewSet):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema(tags=['AM - Room Booking'])
class RoomBookingViewSet(viewsets.ModelViewSet):
    queryset = RoomBooking.objects.all()
    serializer_class = RoomBookingSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        # 自动将当前登录用户设置为 user_id
        serializer.save(user_id=self.request.user)


    def get_queryset(self):
        user = self.request.user
        # 如果是管理员用户，返回所有订单
        if user.is_staff or user.is_superuser:
            return RoomBooking.objects.all()
        # 如果是普通用户，只返回与当前用户相关的订单
        return RoomBooking.objects.filter(user_id=user)

    @action(detail=False,
            methods=['post'],
            url_path='calculate-price',
            permission_classes=[IsAuthenticated],
            serializer_class=AccommodationCalculatePriceSerializer)
    def calculate_price(self, request, *args, **kwargs):
        """
        计算并返回总金额，只需要房间和天数作为参数
        """
        # 使用自定义的序列化器进行数据验证
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 从序列化器中获取经过验证的参数
        room_id = serializer.validated_data.get('room_id')
        number_of_days = serializer.validated_data.get('number_of_days')

        # 获取房间对象
        accommodation = Accommodation.objects.get(id=room_id)
        room = RoomType.objects.get(id=room_id)

        # 计算总金额
        total_price = room.price_per_night * number_of_days

        return Response(
            {
                'accommodation': accommodation.name,
                'room_type': room.room_type,
                'price_per_night': room.price_per_night,
                'number_of_days': number_of_days,
                'total_price': total_price
            }, status=status.HTTP_200_OK
        )

@extend_schema(tags=['AM - Guest Service'])
class GuestServiceViewSet(viewsets.ModelViewSet):
    queryset = GuestService.objects.all()
    serializer_class = GuestServiceSerializer
    permission_classes = [IsAdminOrReadOnly]

@extend_schema(tags=['AM - Feedback Review'])
class FeedbackReviewViewSet(viewsets.ModelViewSet):
    queryset = FeedbackReview.objects.all()
    serializer_class = FeedbackReviewSerializer
    permission_classes = [IsOwnerOrAdmin]

    def perform_create(self, serializer):
        # 自动将当前登录用户设置为 user
        serializer.save(user=self.request.user)
