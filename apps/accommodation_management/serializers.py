# serializers.py

from rest_framework import serializers

from .models import Room, Guest, Booking


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'room_type',
                  'price_per_night', 'is_available']


class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number']


class BookingSerializer(serializers.ModelSerializer):
    guest = GuestSerializer()
    room = RoomSerializer()

    class Meta:
        model = Booking
        fields = ['id', 'guest', 'room', 'check_in',
                  'check_out', 'total_price']

    def create(self, validated_data):
        guest_data = validated_data.pop('guest')
        room_data = validated_data.pop('room')

        # 获取或创建客人
        guest, created = Guest.objects.get_or_create(
            email=guest_data['email'],
            defaults=guest_data
        )

        # 获取房间
        try:
            room = Room.objects.get(id=room_data['id'])
        except Room.DoesNotExist:
            raise serializers.ValidationError("Room does not exist.")

        # 检查房间可用性
        if not room.is_available:
            raise serializers.ValidationError("Room is not available.")

        # 计算总价
        num_nights = (validated_data['check_out']
                      - validated_data['check_in']).days
        total_price = num_nights * room.price_per_night
        validated_data['total_price'] = total_price
        validated_data['guest'] = guest
        validated_data['room'] = room

        booking = Booking.objects.create(**validated_data)
        return booking

    def update(self, instance, validated_data):
        # 可根据需求实现更新逻辑
        return super().update(instance, validated_data)
