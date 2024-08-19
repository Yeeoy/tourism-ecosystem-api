from django.urls import path

import apps.local_attractions_museums.views

urlpatterns = [
    path("", apps.local_attractions_museums.views.index),
    path("hello", apps.local_attractions_museums.views.hello_world),
]
