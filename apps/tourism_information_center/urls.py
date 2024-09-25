from rest_framework.routers import DefaultRouter

from apps.tourism_information_center.views import DestinationViewSet, TourViewSet, EventNotificationViewSet

app_name = 'tourism_information_center'

router = DefaultRouter()
router.register('destinations', DestinationViewSet, basename='destination')
router.register('tours', TourViewSet, basename='tour')
router.register('event-notifications', EventNotificationViewSet, basename='event-notification')

urlpatterns = router.urls
