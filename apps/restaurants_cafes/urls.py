from rest_framework.routers import DefaultRouter

from apps.restaurants_cafes.views import RestaurantViewSet, TableReservationViewSet, MenuViewSet, OnlineOrderViewSet

app_name = 'restaurants_cafes'

router = DefaultRouter()
router.register('restaurants', RestaurantViewSet, basename='restaurant')
router.register('table-reservations', TableReservationViewSet, basename='table-reservation')
router.register('menus', MenuViewSet, basename='menu')
router.register('online-orders', OnlineOrderViewSet, basename='online-order')

urlpatterns = router.urls
