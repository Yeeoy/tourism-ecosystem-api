import logging
from io import BytesIO

import pandas as pd
from django.http import JsonResponse, HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework import generics, authentication, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from apps.customUser.serializers import (
    UserSerializer,
    AuthTokenSerializer
)
from .models import EventLog


# A generic view class for handling POST requests, allowing the creation of new objects
@extend_schema(tags=['User'])
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    log_event = True
    activity_name = "User Registration"


# A generic view class for handling POST requests, allowing the creation of new objects
@extend_schema(tags=['User'])
class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    log_event = True
    activity_name = "User Authentication"

    def post(self, request, *args, **kwargs):
        # Validate and authenticate the user
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Create or retrieve the authentication token for the user
        token, created = Token.objects.get_or_create(user=user)

        # Return response with token and user_id
        return Response({
            'token': token.key,
            'user_id': user.id,
        })


# A generic view class for handling GET and PUT requests, allowing the retrieval and update of objects
@extend_schema(tags=['User'])
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    log_event = True
    activity_name = "User Profile"

    def get_object(self):
        return self.request.user


# Create or configure the logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


def generate_and_download_csv(request):
    try:
        # Step 1: Retrieve all user event data from the database, including `start_time` and `end_time` fields
        events = EventLog.objects.all().values('case_id', 'activity', 'start_time', 'end_time', 'user_id', 'user',
                                               'user_name')
        df = pd.DataFrame(list(events))

        if df.empty:
            logging.error("No events found in the database.")
            return JsonResponse({"message": "No events found."}, status=404)

        # Step 2: Check data format and prepare CSV data
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)  # Reset pointer to the beginning

        logging.info("Successfully created CSV file in memory.")

        # Step 3: Provide the file for user download
        response = HttpResponse(csv_buffer.getvalue(), content_type='application/csv')
        response['Content-Disposition'] = 'attachment; filename="event_log.csv"'
        return response

    except Exception as e:
        # Output detailed error log
        logging.error(f"An error occurred during CSV generation or download: {e}")
        return JsonResponse({"message": f"Internal Server Error: {e}"}, status=500)


class ClearEventLogView(APIView):
    """
    API View to clear all event logs from the database.
    Only accessible to admin users.
    """
    permission_classes = [permissions.AllowAny]

    def delete(self, request, *args, **kwargs):
        # Clear all EventLog data
        deleted, _ = EventLog.objects.all().delete()

        # Return response
        return Response({"message": f"Successfully deleted {deleted} event logs."}, status=status.HTTP_200_OK)
