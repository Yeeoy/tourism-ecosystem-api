from django.urls import path

import apps.restaurants_cafes.views

urlpatterns = [
    path("", apps.restaurants_cafes.views.hello_world),
    path("hello", apps.restaurants_cafes.views.hello_world),
]
