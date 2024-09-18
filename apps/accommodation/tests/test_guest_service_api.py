from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.accommodation.models import GuestService, Accommodation

GUEST_SERVICE_API_URL = reverse('accommodation:guest-service-list')


def create_guest_service(**params):
    return GuestService.objects.create(**params)


def create_user(email='user@example.com', password='password123'):
    return get_user_model().objects.create_user(email=email, password=password)


def detail_url(guest_service_id):
    return reverse('accommodation:guest-service-detail', args=[guest_service_id])


class PublicGuestServiceAPITests(TestCase):
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

    def test_retrieve_guest_services(self):
        create_guest_service(
            accommodation_id=self.accommodation,
            service_name='Test Service',
            price=Decimal('100.00'),
            availability_hours='09:00 - 17:00'
        )

        create_guest_service(
            accommodation_id=self.accommodation,
            service_name='Test Service 2',
            price=Decimal('200.00'),
            availability_hours='09:00 - 17:00'
        )

        res = self.client.get(GUEST_SERVICE_API_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_guest_service_detail(self):
        guest_service = create_guest_service(
            accommodation_id=self.accommodation,
            service_name='Test Service',
            price=Decimal('100.00'),
            availability_hours='09:00 - 17:00'
        )

        url = detail_url(guest_service.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['service_name'], guest_service.service_name)
        self.assertEqual(res.data['price'], str(guest_service.price))
        self.assertEqual(res.data['availability_hours'], guest_service.availability_hours)


class PrivateGuestServiceAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
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

    def test_create_guest_service(self):
        payload = {
            'accommodation_id': self.accommodation.id,
            'service_name': 'Test Service',
            'price': Decimal('100.00'),
            'availability_hours': '09:00 - 17:00'
        }

        res = self.client.post(GUEST_SERVICE_API_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user role to staff
        self.user.is_staff = True
        res = self.client.post(GUEST_SERVICE_API_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['service_name'], payload['service_name'])
        self.assertEqual(res.data['price'], str(payload['price']))
        self.assertEqual(res.data['availability_hours'], payload['availability_hours'])

        guest_service = GuestService.objects.get(id=res.data['id'])
        self.assertEqual(guest_service.accommodation_id, self.accommodation)
        self.assertEqual(guest_service.service_name, payload['service_name'])
        self.assertEqual(guest_service.price, payload['price'])
        self.assertEqual(guest_service.availability_hours, payload['availability_hours'])

    def test_update_guest_service(self):
        guest_service = create_guest_service(
            accommodation_id=self.accommodation,
            service_name='Test Service',
            price=Decimal('100.00'),
            availability_hours='09:00 - 17:00'
        )

        payload = {
            'service_name': 'Updated Service',
            'price': Decimal('200.00'),
            'availability_hours': '10:00 - 18:00'
        }

        url = detail_url(guest_service.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user role to staff
        self.user.is_staff = True
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        guest_service.refresh_from_db()
        self.assertEqual(guest_service.service_name, payload['service_name'])
        self.assertEqual(guest_service.price, payload['price'])
        self.assertEqual(guest_service.availability_hours, payload['availability_hours'])

    def test_delete_guest_service(self):
        guest_service = create_guest_service(
            accommodation_id=self.accommodation,
            service_name='Test Service',
            price=Decimal('100.00'),
            availability_hours='09:00 - 17:00'
        )

        url = detail_url(guest_service.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user role to staff
        self.user.is_staff = True
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(GuestService.objects.filter(id=guest_service.id).exists())
