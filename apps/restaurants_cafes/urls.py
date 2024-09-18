from rest_framework.routers import DefaultRouter

from apps.restaurants_cafes.views import RestaurantViewSet, TableReservationViewSet, MenuViewSet, OnlineOrderViewSet

app_name = 'restaurants_cafes'

router = DefaultRouter()
router.register('restaurant', RestaurantViewSet, basename='restaurant')
router.register('table-reservations', TableReservationViewSet)
router.register('menus', MenuViewSet)
router.register('online-orders', OnlineOrderViewSet)

urlpatterns = router.urls