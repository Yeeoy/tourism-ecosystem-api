from rest_framework import serializers

from .models import (Accommodation, RoomType, RoomBooking, GuestService, FeedbackReview)


class AccommodationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accommodation
        fields = '__all__'
        read_only_fields = ['id', ]


class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = '__all__'
        read_only_fields = ['id', ]


class RoomBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomBooking
        fields = '__all__'
        read_only_fields = ['id', 'total_price']

        def get_total_price(self, obj):
            return obj.calculate_total_price()


class GuestServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestService
        fields = '__all__'
        read_only_fields = ['id', ]


class FeedbackReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackReview
        fields = '__all__'
        read_only_fields = ['id', ]


class AccommodationCalculatePriceSerializer(serializers.Serializer):
    accommodation_id = serializers.IntegerField(required=True)  # 新增 accommodation_id
    room_id = serializers.IntegerField(required=True)
    number_of_days = serializers.IntegerField(required=True)

    def validate_accommodation_id(self, value):
        """
        Validate that the accommodation_id exists in the database.
        """
        if not Accommodation.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Accommodation with id {value} does not exist.")
        return value

    def validate_room_id(self, value):
        """
        Validate that the room_id exists in the database.
        """
        if not RoomType.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Room with id {value} does not exist.")
        return value

    def validate_number_of_days(self, value):
        if value <= 0:
            raise serializers.ValidationError("The number of days must be a positive integer.")
        return value
