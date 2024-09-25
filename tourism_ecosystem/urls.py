from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API Schema and Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'),
         name='api-docs'),
    path('', SpectacularSwaggerView.as_view(url_name='api-schema'),
         name='api-docs'),
    # User-related APIs
    path('api/customUser/', include("apps.customUser.urls")),

    # Accommodation Management APIs
    path('api/accoMgmt/', include("apps.accommodation.urls")),

    # Event Organizer APIs
    path('api/events/', include("apps.event_organizers.urls")),

    # Local Transportation Services APIs
    path('api/transport-services/', include("apps.local_transportation_services.urls")),

    # Dining APIs
    path('api/dining/', include("apps.restaurants_cafes.urls")),

    # Tourism Information Center APIs
    path('api/tourism-info/', include("apps.tourism_information_center.urls")),


]
