from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AttractionViewSet, MuseumViewSet, TicketViewSet,
    TourGuideViewSet, BookingViewSet, EducationContentViewSet
)

app_name = 'local_attractions_museums'  # Ensure this line exists

# 创建默认路由器
router = DefaultRouter()
router.register('attractions', AttractionViewSet)
router.register('museums', MuseumViewSet)
router.register('tickets', TicketViewSet)
router.register('tour-guides', TourGuideViewSet)
router.register('bookings', BookingViewSet)
router.register('education-contents', EducationContentViewSet)

# 连接路由到URLs
urlpatterns = [
    path('api/', include(router.urls)),
]
