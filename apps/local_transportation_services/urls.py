from rest_framework.routers import DefaultRouter

from apps.local_transportation_services.views import TransportationProviderViewSet, RideBookingViewSet, \
    RoutePlanningViewSet, TrafficUpdateViewSet

router = DefaultRouter()
router.register('transportation-provider', TransportationProviderViewSet, basename='transportation-provider')
router.register('ride-booking', RideBookingViewSet, basename='ride-booking')
router.register('route-planning', RoutePlanningViewSet, basename='route-planning')
router.register('traffic-update', TrafficUpdateViewSet, basename='traffic-update')

app_name = 'local_transportation_services'
urlpatterns = router.urls
