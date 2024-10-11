from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.accommodation.models import Accommodation, RoomType, RoomBooking, GuestService, FeedbackReview
from apps.accommodation.serializers import AccommodationSerializer, RoomTypeSerializer, \
    RoomBookingSerializer, AccommodationCalculatePriceSerializer, GuestServiceSerializer, FeedbackReviewSerializer
from tourism_ecosystem.permissions import IsAdminOrReadOnly, IsOwnerOrAdmin


@extend_schema(tags=['AM - Accommodation'])
class AccommodationViewSet(viewsets.ModelViewSet):
    queryset = Accommodation.objects.all()
    serializer_class = AccommodationSerializer
    permission_classes = [IsAdminOrReadOnly]
    log_event = True
    activity_name = "Accommodation Management"


@extend_schema(tags=['AM - Room Type'])
class RoomTypeViewSet(viewsets.ModelViewSet):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer
    permission_classes = [IsAdminOrReadOnly]
    log_event = True
    activity_name = "Room Type Management"


@extend_schema(tags=['AM - Room Booking'])
class RoomBookingViewSet(viewsets.ModelViewSet):
    queryset = RoomBooking.objects.all()
    serializer_class = RoomBookingSerializer
    permission_classes = [IsAdminOrReadOnly]
    log_event = True

    def perform_create(self, serializer):
        # Automatically sets the currently logged in user to user_id
        serializer.save(user_id=self.request.user)

    def get_queryset(self):
        user = self.request.user
        # If admin user, return all orders
        if user.is_staff or user.is_superuser:
            return RoomBooking.objects.all()
        # In case of a regular user, only orders related to the current user are returned
        return RoomBooking.objects.filter(user_id=user)

    @action(detail=False,
            methods=['post'],
            url_path='calculate-price',
            permission_classes=[IsAuthenticated],
            serializer_class=AccommodationCalculatePriceSerializer)
    def calculate_price(self, request, *args, **kwargs):
        """
        Calculates and returns the total amount with only the room and days as parameters
        """
        # Data validation using custom serializers
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Getting Validated Parameters from the Serializer
        room_id = serializer.validated_data.get('room_id')
        number_of_days = serializer.validated_data.get('number_of_days')

        # Get the room object
        accommodation = Accommodation.objects.get(id=room_id)
        room = RoomType.objects.get(id=room_id)

        # Calculation of the total amount
        total_price = room.price_per_night * number_of_days

        return Response(
            {
                'accommodation': accommodation.name,
                'room_type': room.room_type,
                'price_per_night': room.price_per_night,
                'number_of_days': number_of_days,
                'total_price': total_price
            }, status=status.HTTP_200_OK
        )


@extend_schema(tags=['AM - Guest Service'])
class GuestServiceViewSet(viewsets.ModelViewSet):
    queryset = GuestService.objects.all()
    serializer_class = GuestServiceSerializer
    permission_classes = [IsAdminOrReadOnly]
    log_event = True
    activity_name = "Guest Service Management"


@extend_schema(tags=['AM - Feedback Review'])
class FeedbackReviewViewSet(viewsets.ModelViewSet):
    queryset = FeedbackReview.objects.all()
    serializer_class = FeedbackReviewSerializer
    permission_classes = [IsOwnerOrAdmin]
    log_event = True
    activity_name = "Feedback Review"

    def perform_create(self, serializer):
        # Automatically sets the current login user to user
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'],
            url_path='accommodation/(?P<accommodation_id>[^/.]+)',
            permission_classes=[AllowAny])
    def get_feedback_by_accommodation(self, request, accommodation_id=None):
        """
        Retrieve all feedback ratings for a given accommodation by accommodation_id
        """
        if not accommodation_id:
            return Response({'error': 'The accommodation_id parameter is required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        feedbacks = self.get_feedbacks_by_accommodation(accommodation_id)
        serializer = self.get_serializer(feedbacks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_feedbacks_by_accommodation(self, accommodation_id):
        """
        Helper method to get feedbacks by accommodation_id
        """
        return self.queryset.filter(accommodation_id=accommodation_id)
