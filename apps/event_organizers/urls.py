from django.urls import path

import apps.event_organizers.views

urlpatterns = [
    path("", apps.event_organizers.views.index),
    path("hello", apps.event_organizers.views.hello_world),
]
