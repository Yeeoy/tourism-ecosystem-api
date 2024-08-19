from django.urls import path

import apps.retail_solutions.views

urlpatterns = [
    path("", apps.retail_solutions.views.hello_world),
    path("hello", apps.retail_solutions.views.hello_world),
]
