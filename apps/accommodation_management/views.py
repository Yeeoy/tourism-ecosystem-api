# Create your views here.

from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Room, Guest, Booking
from .serializers import RoomSerializer, GuestSerializer, BookingSerializer


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 检查预订冲突
        room_id = request.data.get('room', {}).get('id')
        check_in = request.data.get('check_in')
        check_out = request.data.get('check_out')

        if Booking.objects.filter(
                room_id=room_id,
                check_in__lt=check_out,
                check_out__gt=check_in
        ).exists():
            return Response({
                "error": "Booking conflict detected. "
                         "The room is already booked for the selected dates."},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)
