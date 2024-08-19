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

urlpatterns = [
    path("admin", admin.site.urls),
    path("", include("apps.accommodation_management.urls")),
    path("accommodation_management/", include("apps.accommodation_management.urls")),
    path("event_organizers/", include("apps.event_organizers.urls")),
    path("local_attractions_museums/", include("apps.local_attractions_museums.urls")),
    path("local_transportation_services/", include("apps.local_transportation_services.urls")),
    path("outdoor_activity_centers/", include("apps.outdoor_activity_centers.urls")),
    path("restaurants_cafes/", include("apps.restaurants_cafes.urls")),
    path("retail_solutions/", include("apps.retail_solutions.urls")),
    path("tour_event_services/", include("apps.tour_event_services.urls")),
    path("visitor_info_center/", include("apps.visitor_info_center.urls")),

]
