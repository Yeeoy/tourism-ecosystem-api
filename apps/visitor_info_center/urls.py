from django.urls import path

import apps.visitor_info_center.views

urlpatterns = [
    path("", apps.visitor_info_center.views.hello_world),
    path("hello", apps.visitor_info_center.views.hello_world),
]
