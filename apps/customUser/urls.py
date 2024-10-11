from django.urls import path

from apps.customUser import views
from apps.customUser.views import ClearEventLogView

app_name = 'customUser'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('download_csv/', views.generate_and_download_csv, name='download_csv'),
    path('clear_event_logs/', ClearEventLogView.as_view(), name='clear_event_logs'),

]
