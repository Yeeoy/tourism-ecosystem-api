from rest_framework import viewsets
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated,
                                        AllowAny, IsAdminUser)

from tourism_ecosystem.Permissions import IsOwnerOrAdmin
from .models import (Attraction, Museum, Ticket,
                     TourGuide, Booking, EducationContent)
from .serializers import (
    AttractionSerializer, MuseumSerializer, TicketSerializer,
    TourGuideSerializer, BookingSerializer, EducationContentSerializer
)


# 景点视图集
class AttractionViewSet(viewsets.ModelViewSet):
    queryset = Attraction.objects.all()
    serializer_class = AttractionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # 未登录用户只能查看，管理员可管理


# 博物馆视图集
class MuseumViewSet(viewsets.ModelViewSet):
    queryset = Museum.objects.all()
    serializer_class = MuseumSerializer
    permission_classes = [IsAuthenticated]  # 只有已登录用户才能查看，管理员有完全权限


# 门票视图集
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [AllowAny]  # 所有用户都可以访问
    # 如果需要区分用户行为，可以添加额外逻辑


# 导游视图集
class TourGuideViewSet(viewsets.ModelViewSet):
    queryset = TourGuide.objects.all()
    serializer_class = TourGuideSerializer
    permission_classes = [IsAdminUser]  # 只有管理员可以访问


# 预订视图集
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]  # 使用自定义权限


# 教育内容视图集
class EducationContentViewSet(viewsets.ModelViewSet):
    queryset = EducationContent.objects.all()
    serializer_class = EducationContentSerializer
    permission_classes = [IsAdminUser]  # 只有管理员可以访问
