from django.urls import path

import apps.accommodation_management.views

urlpatterns = [
    path("", apps.accommodation_management.views.index),
    path("hello", apps.accommodation_management.views.hello_world),
]
