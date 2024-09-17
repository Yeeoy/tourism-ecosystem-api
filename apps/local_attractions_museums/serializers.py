from rest_framework import serializers

from .models import (Attraction, Museum, Ticket,
                     TourGuide, Booking, EducationContent)


class AttractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attraction
        fields = '__all__'


class MuseumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Museum
        fields = '__all__'

    def create(self, validated_data):
        attractions_data = validated_data.pop('attractions', [])
        museum = Museum.objects.create(**validated_data)
        museum.attractions.set(attractions_data)
        return museum


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'


class TourGuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourGuide
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'


class EducationContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationContent
        fields = '__all__'
