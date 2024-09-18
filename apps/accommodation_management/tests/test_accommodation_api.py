from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.accommodation_management.models import Accommodation


ACCOMMODATION_URL = reverse('accommodation_management:accommodation-list')

def create_accommodation(**params):
    return Accommodation.objects.create(**params)

def create_user(**params):
    return get_user_model().objects.create_user(**params)

def detail_url(accommodation_id):
    return reverse(
        'accommodation_management:accommodation-detail',
        args=[accommodation_id]
    )

class PublicAccommodationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_retrieve_accommodations(self):
        create_accommodation(
            name = 'Test Accommodation',
            location = 'Test Location',
            star_rating = 4,
            total_rooms = 100,
            amenities = 'Test amenities',
            type = 'Test type',
            check_in_time = '09:00:00',
            check_out_time = '17:00:00',
            contact_info = 'Test contact info'
        )

        create_accommodation(
            name = 'Test Accommodation 2',
            location = 'Test Location 2',
            star_rating = 3,
            total_rooms = 200,
            amenities = 'Test amenities 2',
            type = 'Test type 2',
            check_in_time = '09:00:00',
            check_out_time = '17:00:00',
            contact_info = 'Test contact info 2'
        )

        res = self.client.get(ACCOMMODATION_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

        self.assertEqual(res.data[0]['name'], 'Test Accommodation')
        self.assertEqual(res.data[1]['name'], 'Test Accommodation 2')

    def test_retrieve_accommodation_detail(self):
        accommodation = create_accommodation(
            name = 'Test Accommodation',
            location = 'Test Location',
            star_rating = 4,
            total_rooms = 100,
            amenities = 'Test amenities',
            type = 'Test type',
            check_in_time = '09:00:00',
            check_out_time = '17:00:00',
            contact_info = 'Test contact info'
        )

        res = self.client.get(detail_url(accommodation.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], accommodation.name)
        self.assertEqual(res.data['location'], accommodation.location)
        self.assertEqual(res.data['star_rating'], accommodation.star_rating)
        self.assertEqual(res.data['total_rooms'], accommodation.total_rooms)
        self.assertEqual(res.data['amenities'], accommodation.amenities)
        self.assertEqual(res.data['type'], accommodation.type)
        self.assertEqual(res.data['check_in_time'], accommodation.check_in_time)
        self.assertEqual(res.data['check_out_time'], accommodation.check_out_time)
        self.assertEqual(res.data['contact_info'], accommodation.contact_info)

class PrivateAccommodationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com',
            password='password123'
        )
        self.client.force_authenticate(self.user)

    def test_create_accommodation(self):
        payload = {
            'name': 'Test Accommodation',
            'location': 'Test Location',
            'star_rating': 4,
            'total_rooms': 100,
            'amenities': 'Test amenities',
            'type': 'Test type',
            'check_in_time': '09:00:00',
            'check_out_time': '17:00:00',
            'contact_info': 'Test contact info'
        }
        res = self.client.post(ACCOMMODATION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user role to staff
        self.user.is_staff = True
        res = self.client.post(ACCOMMODATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        accommodation = Accommodation.objects.get(id=res.data['id'])
        self.assertEqual(accommodation.name, payload['name'])
        self.assertEqual(accommodation.location, payload['location'])

    def test_update_accommodation(self):
        accommodation = create_accommodation(
            name = 'Test Accommodation',
            location = 'Test Location',
            star_rating = 4,
            total_rooms = 100,
            amenities = 'Test amenities',
            type = 'Test type',
            check_in_time = '09:00:00',
            check_out_time = '17:00:00',
            contact_info = 'Test contact info'
        )

        payload = {
            'name': 'Updated Accommodation',
            'location': 'Updated Location',
            'star_rating': 5,
            'total_rooms': 200,
            'amenities': 'Updated amenities',
            'type': 'Updated type',
            'check_in_time': '10:00:00',
            'check_out_time': '18:00:00',
            'contact_info': 'Updated contact info'
        }

        res = self.client.patch(detail_url(accommodation.id), payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user role to staff
        self.user.is_staff = True
        res = self.client.patch(detail_url(accommodation.id), payload)

        accommodation.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(accommodation.name, payload['name'])
        self.assertEqual(accommodation.location, payload['location'])
        self.assertEqual(accommodation.star_rating, payload['star_rating'])
        self.assertEqual(accommodation.total_rooms, payload['total_rooms'])
        self.assertEqual(accommodation.amenities, payload['amenities'])
        self.assertEqual(accommodation.type, payload['type'])
        # 将 accommodation.check_in_time 转换为字符串
        self.assertEqual(accommodation.check_in_time.strftime('%H:%M:%S'), payload['check_in_time'])
        self.assertEqual(accommodation.check_out_time.strftime('%H:%M:%S'), payload['check_out_time'])
        self.assertEqual(accommodation.contact_info, payload['contact_info'])

    def test_delete_accommodation(self):
        accommodation = create_accommodation(
            name = 'Test Accommodation',
            location = 'Test Location',
            star_rating = 4,
            total_rooms = 100,
            amenities = 'Test amenities',
            type = 'Test type',
            check_in_time = '09:00:00',
            check_out_time = '17:00:00',
            contact_info = 'Test contact info'
        )

        res = self.client.delete(detail_url(accommodation.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user role to staff
        self.user.is_staff = True
        res = self.client.delete(detail_url(accommodation.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Accommodation.objects.filter(id=accommodation.id).exists())