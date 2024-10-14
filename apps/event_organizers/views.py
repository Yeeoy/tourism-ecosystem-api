from decimal import Decimal

from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated)
from rest_framework.response import Response

from tourism_ecosystem.permissions import IsAdminOrReadOnly
from tourism_ecosystem.responses import CustomResponse
from tourism_ecosystem.views import LoggingViewSet
from .models import (Event, VenueBooking, EventPromotion)
from .serializers import (EventSerializer, VenueBookingSerializer,
                          EventPromotionSerializer, EventBookingCalculatePriceSerializer)


@extend_schema(tags=['EO - Event'])
class EventViewSet(LoggingViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrReadOnly]
    activity_name = "Event"


@extend_schema(tags=['EO - Venue Booking'])
class VenueBookingViewSet(LoggingViewSet):
    queryset = VenueBooking.objects.all()
    serializer_class = VenueBookingSerializer
    permission_classes = [IsAuthenticated]
    activity_name = "Venue Booking"

    def perform_create(self, serializer):
        # Automatically set the current logged-in user as user_id
        print(self.request.user)
        serializer.save(user_id=self.request.user)

    def get_queryset(self):
        user = self.request.user
        # If the user is an admin, return all bookings
        if user.is_staff or user.is_superuser:
            return VenueBooking.objects.all()
        # If the user is a regular user, return only the bookings related to the current user
        return VenueBooking.objects.filter(user_id=user)

    @action(detail=False,
            methods=['post'],
            url_path='calculate-price',
            permission_classes=[IsAuthenticated],
            serializer_class=EventBookingCalculatePriceSerializer)
    def calculate_price(self, request, *args, **kwargs):
        """
        Calculate and return the total amount, only event and ticket count are required as parameters
        """
        # Use custom serializer for data validation
        self.activity_name = "Calculate Event Price"
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get validated parameters from the serializer
        event_id = serializer.validated_data.get('event')
        number_of_tickets = serializer.validated_data.get('number_of_tickets')
        discount = 1  # Default discount is 1
        discount_amount = 0
        try:
            # Get the event object
            event = Event.objects.get(id=event_id)
            # Use Decimal for monetary calculations
            ticket_price = Decimal(event.entry_fee)
            # Ensure all monetary calculations use Decimal
            base_amount = ticket_price * Decimal(number_of_tickets)

            # Check if there is a promotion
            promotion = EventPromotion.objects.filter(
                event=event,
                promotion_start_date__lte=timezone.now().date(),
                promotion_end_date__gte=timezone.now().date()
            ).order_by('-discount').first()

            if promotion:
                discount = Decimal(promotion.discount)

                # Determine if the discount is a decimal or a percentage
                if discount <= 1:
                    # If the discount is less than 1, use it directly as a decimal
                    discount_amount = base_amount * (1 - discount)
                else:
                    # Throw an error if the discount exceeds 1
                    return Response(
                        {"detail": "Discount value cannot be greater than 1."},
                        status=status.HTTP_400_BAD_REQUEST)

                total_amount = base_amount - discount_amount
            else:
                total_amount = base_amount

            # Return the calculated total amount
            return Response(
                {"event": event_id,
                 "ticket_price": ticket_price,
                 "number_of_tickets": number_of_tickets,
                 "discount": discount,
                 "base_amount": base_amount,
                 "total_amount": total_amount,
                 "discount_amount": discount_amount
                 }, status=status.HTTP_200_OK)

        except Event.DoesNotExist:
            return CustomResponse.error(
                "Event not found.",
                status.HTTP_404_NOT_FOUND
            )


@extend_schema(tags=['EO - Event Promotion'])
class EventPromotionViewSet(LoggingViewSet):
    queryset = EventPromotion.objects.all()
    serializer_class = EventPromotionSerializer
    permission_classes = [IsAdminOrReadOnly]
    activity_name = "Event Promotion"
