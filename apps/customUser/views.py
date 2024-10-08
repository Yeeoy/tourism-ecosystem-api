from drf_spectacular.utils import extend_schema
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings

from apps.customUser.serializers import (
    UserSerializer,
    AuthTokenSerializer
)


# A generic view class for handling POST requests, allowing the creation of new objects
@extend_schema(tags=['User'])
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


# A generic view class for handling POST requests, allowing the creation of new objects
@extend_schema(tags=['User'])
class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

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

    def get_object(self):
        return self.request.user
