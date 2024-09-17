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
    path('api/user/', include("apps.user.urls")),

    # Accommodation Management APIs
    path('api/accommodation/', include("apps.accommodation_management.urls")),

    # Event Organizer APIs
    path('api/events/', include("apps.event_organizers.urls")),

    # Local Attractions and Museums APIs
    path('api/attractions/', include("apps.local_attractions_museums.urls")),

    # Dining APIs
    path('api/dining/', include("apps.restaurants_cafes.urls")),

    # Tour and Event Services APIs
    path('api/tours/', include("apps.tour_event_services.urls")),
]
