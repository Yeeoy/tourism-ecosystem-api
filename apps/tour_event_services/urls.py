from django.urls import path

import apps.tour_event_services.views

urlpatterns = [
    path("", apps.tour_event_services.views.hello_world),
    path("hello", apps.tour_event_services.views.hello_world),
]
