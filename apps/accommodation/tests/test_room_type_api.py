from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.accommodation.models import RoomType, Accommodation

ROOM_TYPE_URL = reverse('accommodation:room-type-list')


def create_room_type(**params):
    return RoomType.objects.create(**params)


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def detail_url(room_type_id):
    return reverse(
        'accommodation:room-type-detail',
        args=[room_type_id]
    )


class PublicRoomTypeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
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

    def test_retrieve_room_types(self):
        create_room_type(
            accommodation_id=self.accommodation,
            room_type='Test Room Type',
            price_per_night=100.00,
            max_occupancy=2,
            availability=True
        )

        create_room_type(
            accommodation_id=self.accommodation,
            room_type='Test Room Type 2',
            price_per_night=200.00,
            max_occupancy=4,
            availability=True
        )

        res = self.client.get(ROOM_TYPE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

        self.assertEqual(res.data[0]['room_type'], 'Test Room Type')
        self.assertEqual(res.data[1]['room_type'], 'Test Room Type 2')

    def test_retrieve_room_type_detail(self):
        room_type = create_room_type(
            accommodation_id=self.accommodation,
            room_type='Test Room Type',
            price_per_night=Decimal('100.00'),
            max_occupancy=2,
            availability=True
        )

        res = self.client.get(detail_url(room_type.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['room_type'], room_type.room_type)
        self.assertEqual(res.data['price_per_night'], str(room_type.price_per_night))
        self.assertEqual(res.data['max_occupancy'], room_type.max_occupancy)
        self.assertEqual(res.data['availability'], room_type.availability)


class PrivateRoomTypeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com',
            password='password123'
        )
        self.client.force_authenticate(self.user)

    def test_create_room_type(self):
        accommodation = Accommodation.objects.create(
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

        payload = {
            'accommodation_id': accommodation.id,
            'room_type': 'Test Room Type',
            'price_per_night': 100.00,
            'max_occupancy': 2,
            'availability': True
        }

        res = self.client.post(ROOM_TYPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change to admin role
        self.user.is_staff = True
        res = self.client.post(ROOM_TYPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        room_type = RoomType.objects.get(id=res.data['id'])
        self.assertEqual(room_type.accommodation_id, accommodation)

    def test_update_room_type(self):
        accommodation = Accommodation.objects.create(
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

        room_type = create_room_type(
            accommodation_id=accommodation,
            room_type='Test Room Type',
            price_per_night=Decimal('100.00'),
            max_occupancy=2,
            availability=True
        )

        payload = {
            'accommodation_id': accommodation.id,
            'room_type': 'Test Room Type Updated',
            'price_per_night': Decimal('200.00'),
            'max_occupancy': 4,
            'availability': False
        }

        url = detail_url(room_type.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change to admin role
        self.user.is_staff = True
        self.client.patch(url, payload)

        room_type.refresh_from_db()
        self.assertEqual(room_type.room_type, payload['room_type'])
        self.assertEqual(room_type.price_per_night, Decimal(payload['price_per_night']))
        self.assertEqual(room_type.max_occupancy, payload['max_occupancy'])
        self.assertEqual(room_type.availability, payload['availability'])

    def test_delete_room_type(self):
        accommodation = Accommodation.objects.create(
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

        room_type = create_room_type(
            accommodation_id=accommodation,
            room_type='Test Room Type',
            price_per_night=Decimal('100.00'),
            max_occupancy=2,
            availability=True
        )

        url = detail_url(room_type.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change to admin role
        self.user.is_staff = True
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(RoomType.objects.filter(id=room_type.id).exists())
