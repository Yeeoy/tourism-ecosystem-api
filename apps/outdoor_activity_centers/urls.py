from django.urls import path

import apps.outdoor_activity_centers.views

urlpatterns = [
    path("", apps.outdoor_activity_centers.views.hello_world),
    path("hello", apps.outdoor_activity_centers.views.hello_world),
]
