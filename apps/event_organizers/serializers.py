from decimal import Decimal

from rest_framework import serializers

from .models import (Event, VenueBooking, EventPromotion)


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'venue', 'description',
                  'event_date', 'start_time', 'end_time',
                  'entry_fee', 'max_participants']

        read_only_fields = ['id', ]


class VenueBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueBooking
        fields = '__all__'
        read_only_fields = ['id', 'total_amount', 'discount_amount', 'user_id']

    def get_total_amount(self, obj):
        return obj.calculate_total_amount()


class EventPromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPromotion
        fields = ('id', 'event', 'promotion_start_date', 'promotion_end_date', 'discount')
        read_only_fields = ['id', ]

    def validate_discount(self, value):
        return Decimal(str(value))


class EventBookingCalculatePriceSerializer(serializers.Serializer):
    event = serializers.IntegerField(required=True)
    number_of_tickets = serializers.IntegerField(required=True)

    def validate_number_of_tickets(self, value):
        if value <= 0:
            raise serializers.ValidationError("The number of tickets must be a positive integer.")
        return value
