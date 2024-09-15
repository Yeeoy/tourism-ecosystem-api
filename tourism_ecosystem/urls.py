"""
URL configuration for tourism_ecosystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(),
         name='api-schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'),
         name='api-docs'),
    path('', SpectacularSwaggerView.as_view(url_name='api-schema'),
         name='api-docs'),
    path("api/user/", include("apps.user.urls")),
    path("api/accom/", include("apps.accommodation_management.urls")),
    path("events/", include("apps.event_organizers.urls")),
    path("attractions/", include("apps.local_attractions_museums.urls")),
    path("dining/", include("apps.restaurants_cafes.urls")),
    path("tours/", include("apps.tour_event_services.urls")),

]
