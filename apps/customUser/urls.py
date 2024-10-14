# apps/customUser/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CreateUserView,
    CreateTokenView,
    ManageUserView,
    EventLogListView,
    GenerateAndDownloadCSV,
    ClearEventLogView,
    GenerateAndDownloadXES,
)

router = DefaultRouter()
# Only register ViewSets with the router
# router.register('your-viewset', YourViewSet)

urlpatterns = [
    path('create/', CreateUserView.as_view(), name='create-user'),
    path('token/', CreateTokenView.as_view(), name='token'),
    path('me/', ManageUserView.as_view(), name='manage-user'),
    path('event_logs/', EventLogListView.as_view(), name='event-log-list'),
    path('download_csv/', GenerateAndDownloadCSV.as_view(), name='download-csv'),
    path('clear_event_logs/', ClearEventLogView.as_view(), name='clear-event-logs'),
    path('download_xes/', GenerateAndDownloadXES.as_view(), name='download-xes'),
    path('', include(router.urls)),  # Include this only if you have ViewSets registered
]
