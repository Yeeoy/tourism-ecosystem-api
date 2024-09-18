from rest_framework import serializers

from apps.local_transportation_services.models import (TransportationProvider, RideBooking,
                                                       RoutePlanning, TrafficUpdate)


class TransportationServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportationProvider
        fields = '__all__'


class RideBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideBooking
        fields = '__all__'
        read_only_fields = ['id', ]


class RoutePlanningSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutePlanning
        fields = '__all__'
        read_only_fields = ['id', ]


class TrafficUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficUpdate
        fields = '__all__'
        read_only_fields = ['id', ]
