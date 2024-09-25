from rest_framework import serializers

from apps.tourism_information_center.models import Destination, Tour, EventNotification


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = '__all__'
        read_only_fields = ['id']


class TourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tour
        fields = '__all__'
        read_only_fields = ['id']


class EventNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventNotification
        fields = '__all__'
        read_only_fields = ['id']
