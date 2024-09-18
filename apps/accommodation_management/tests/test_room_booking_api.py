from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.accommodation_management.models import RoomBooking, Accommodation, RoomType

ROOM_BOOKING_URL = reverse('accommodation_management:room-booking-list')


def create_room_booking(**params):
    return RoomBooking.objects.create(**params)


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def detail_url(room_booking_id):
    return reverse(
        'accommodation_management:room-booking-detail',
        args=[room_booking_id]
    )


class PublicRoomBookingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com',
            password='password123'
        )
        self.client.force_authenticate(self.user)

        self.accommodation = Accommodation.objects.create(
            name='Test Accommodation',
            location='Test Location',
            star_rating=4,
            total_rooms=100,
            amenities='Test amenities',
            type='Test type',
            check_in_time='09:00:00',
            check_out_time='17:00:00',
            contact_info='Test contact info'
        )

        self.room = RoomType.objects.create(
            accommodation_id=self.accommodation,
            room_type='Test Room Type',
            price_per_night=Decimal('100.00'),
            max_occupancy=20,
            availability=True
        )

        self.room2 = RoomType.objects.create(
            accommodation_id=self.accommodation,
            room_type='Test Room Type',
            price_per_night=Decimal('200.00'),
            max_occupancy=20,
            availability=True
        )

    def test_retrieve_room_bookings(self):
        user2 = create_user(
            email='test2@example.com',
            password='password123'
        )

        create_room_booking(
            room_type_id=self.room,
            accommodation_id=self.accommodation,
            user_id=user2,
            check_in_date='2021-03-01',
            check_out_date='2021-03-03',
            booking_status=False,
            payment_status=False
        )

        create_room_booking(
            room_type_id=self.room2,
            accommodation_id=self.accommodation,
            user_id=self.user,
            check_in_date='2021-03-04',
            check_out_date='2021-03-06',
            booking_status=False,
            payment_status=False
        )

        res = self.client.get(ROOM_BOOKING_URL)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

        self.assertEqual(res.data[0]['total_price'], '400.00')

        self.user.is_staff = True
        res = self.client.get(ROOM_BOOKING_URL)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_room_booking_detail(self):
        user2 = create_user(
            email='test2@example.com',
            password='password123'
        )

        room_booking = create_room_booking(
            room_type_id=self.room,
            accommodation_id=self.accommodation,
            user_id=user2,
            check_in_date='2021-03-01',
            check_out_date='2021-03-03',
            booking_status=False,
            payment_status=False
        )

        room_booking2 = create_room_booking(
            room_type_id=self.room,
            accommodation_id=self.accommodation,
            user_id=self.user,
            check_in_date='2021-03-04',
            check_out_date='2021-03-06',
            booking_status=False,
            payment_status=False
        )

        res = self.client.get(detail_url(room_booking.id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        res = self.client.get(detail_url(room_booking2.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['total_price'], '200.00')

    def test_create_room_booking(self):
        payload = {
            'room_type_id': self.room.id,
            'accommodation_id': self.accommodation.id,
            'user_id': self.user.id,
            'check_in_date': '2021-03-01',
            'check_out_date': '2021-03-03',
            'booking_status': False,
            'payment_status': False
        }

        res = self.client.post(ROOM_BOOKING_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user role to staff
        self.user.is_staff = True
        res = self.client.post(ROOM_BOOKING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['total_price'], '200.00')

class PrivateRoomBookingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com',
            password='password123'
        )
        self.client.force_authenticate(self.user)

        self.accommodation = Accommodation.objects.create(
            name='Test Accommodation',
            location='Test Location',
            star_rating=4,
            total_rooms=100,
            amenities='Test amenities',
            type='Test type',
            check_in_time='09:00:00',
            check_out_time='17:00:00',
            contact_info='Test contact info'
        )

        self.room = RoomType.objects.create(
            accommodation_id=self.accommodation,
            room_type='Test Room Type',
            price_per_night=Decimal('100.00'),
            max_occupancy=20,
            availability=True
        )

    def test_create_room_booking(self):
        payload = {
            'room_type_id': self.room.id,
            'accommodation_id': self.accommodation.id,
            'user_id': self.user.id,
            'check_in_date': '2021-03-01',
            'check_out_date': '2021-03-03',
            'booking_status': False,
            'payment_status': False
        }

        res = self.client.post(ROOM_BOOKING_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user role to staff
        self.user.is_staff = True
        res = self.client.post(ROOM_BOOKING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['total_price'], '200.00')

    def test_update_room_booking(self):
        user2 = create_user(
            email='test2@example.com',
            password='password123'
        )

        room_booking = create_room_booking(
            room_type_id=self.room,
            accommodation_id=self.accommodation,
            user_id=user2,
            check_in_date='2021-03-01',
            check_out_date='2021-03-03',
            booking_status=False,
            payment_status=False
        )

        payload = {
            'room_type_id': self.room.id,
            'accommodation_id': self.accommodation.id,
            'user_id': user2.id,
            'check_in_date': '2021-03-01',
            'check_out_date': '2021-03-03',
            'booking_status': True,
            'payment_status': False
        }

        res = self.client.patch(detail_url(room_booking.id), payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user role to staff
        self.user.is_staff = True
        res = self.client.patch(detail_url(room_booking.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['booking_status'], True)
        self.assertEqual(res.data['payment_status'], False)

    def test_delete_room_booking(self):
        user2 = create_user(
            email='test2@example.com',
            password='password123'
        )

        room_booking = create_room_booking(
            room_type_id=self.room,
            accommodation_id=self.accommodation,
            user_id=user2,
            check_in_date='2021-03-01',
            check_out_date='2021-03-03',
            booking_status=False,
            payment_status=False
        )

        res = self.client.delete(detail_url(room_booking.id))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user role to staff
        self.user.is_staff = True
        res = self.client.delete(detail_url(room_booking.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)






