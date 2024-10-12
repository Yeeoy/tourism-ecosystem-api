from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.accommodation.models import RoomType

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

    def test_retrieve_room_types(self):
        create_room_type(
            room_type='Test Room Type',
            price_per_night=100.00,
            max_occupancy=2,
            availability=True
        )

        create_room_type(
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
        payload = {
            'room_type': 'Test Room Type',
            'price_per_night': Decimal('100.00'),
            'max_occupancy': 2,
            'availability': True
        }

        res = self.client.post(ROOM_TYPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change the user to a staff user
        self.user.is_staff = True
        res = self.client.post(ROOM_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        room_type = RoomType.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(room_type, key))

    def test_update_room_type(self):
        room_type = create_room_type(
            room_type='Test Room Type',
            price_per_night=Decimal('100.00'),
            max_occupancy=2,
            availability=True
        )

        payload = {
            'room_type': 'Updated Room Type',
            'price_per_night': Decimal('200.00'),
            'max_occupancy': 4,
            'availability': False
        }

        res = self.client.patch(detail_url(room_type.id), payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change the user to a staff user
        self.user.is_staff = True
        res = self.client.patch(detail_url(room_type.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        room_type.refresh_from_db()
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(room_type, key))

    def test_delete_room_type(self):
        room_type = create_room_type(
            room_type='Test Room Type',
            price_per_night=Decimal('100.00'),
            max_occupancy=2,
            availability=True
        )

        res = self.client.delete(detail_url(room_type.id))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change the user to a staff user
        self.user.is_staff = True
        res = self.client.delete(detail_url(room_type.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(RoomType.objects.filter(id=room_type.id).exists())
