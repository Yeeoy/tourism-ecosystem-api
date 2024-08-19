from django.urls import path

import apps.local_transportation_services.views

urlpatterns = [
    path("", apps.local_transportation_services.views.hello_world),
    path("hello", apps.local_transportation_services.views.hello_world),
]
