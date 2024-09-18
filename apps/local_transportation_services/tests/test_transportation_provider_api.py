from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.local_transportation_services.models import TransportationProvider

TRANSPORTATION_PROVIDER_API_URL = reverse('local_transportation_services:transportation-provider-list')


def create_transportation_provider(**params):
    return TransportationProvider.objects.create(**params)


def create_user(email='user@example.com', password='password123'):
    return get_user_model().objects.create_user(email=email, password=password)


def detail_url(transportation_provider_id):
    return reverse('local_transportation_services:transportation-provider-detail', args=[transportation_provider_id])


class PublicTransportationProviderAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_retrieve_transportation_providers(self):
        create_transportation_provider(
            name='Test Transportation Provider',
            service_type='Test Service Type',
            base_fare=Decimal('100.00'),
            price_per_km=Decimal('10.00'),
            contact_info='Test contact info'
        )

        create_transportation_provider(
            name='Test Transportation Provider 2',
            service_type='Test Service Type 2',
            base_fare=Decimal('200.00'),
            price_per_km=Decimal('20.00'),
            contact_info='Test contact info 2'
        )

        res = self.client.get(TRANSPORTATION_PROVIDER_API_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_transportation_provider_detail(self):
        transportation_provider = create_transportation_provider(
            name='Test Transportation Provider',
            service_type='Test Service Type',
            base_fare=Decimal('100.00'),
            price_per_km=Decimal('10.00'),
            contact_info='Test contact info'
        )

        res = self.client.get(detail_url(transportation_provider.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], transportation_provider.name)
        self.assertEqual(res.data['service_type'], transportation_provider.service_type)
        self.assertEqual(res.data['base_fare'], str(transportation_provider.base_fare))
        self.assertEqual(res.data['price_per_km'], str(transportation_provider.price_per_km))
        self.assertEqual(res.data['contact_info'], transportation_provider.contact_info)


class PrivateTransportationProviderAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_create_transportation_provider(self):
        payload = {
            'name': 'Test Transportation Provider',
            'service_type': 'Test Service Type',
            'base_fare': Decimal('100.00'),
            'price_per_km': Decimal('10.00'),
            'contact_info': 'Test contact info'
        }

        res = self.client.post(TRANSPORTATION_PROVIDER_API_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user to staff
        self.user.is_staff = True

        res = self.client.post(TRANSPORTATION_PROVIDER_API_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        transportation_provider = TransportationProvider.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(transportation_provider, key))

    def test_update_transportation_provider(self):
        transportation_provider = create_transportation_provider(
            name='Test Transportation Provider',
            service_type='Test Service Type',
            base_fare=Decimal('100.00'),
            price_per_km=Decimal('10.00'),
            contact_info='Test contact info'
        )

        payload = {
            'name': 'Updated Name',
            'service_type': 'Updated Service Type',
            'base_fare': Decimal('200.00'),
            'price_per_km': Decimal('20.00'),
            'contact_info': 'Updated contact info'
        }

        url = detail_url(transportation_provider.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user to staff
        self.user.is_staff = True
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        transportation_provider.refresh_from_db()
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(transportation_provider, key))

    def test_delete_transportation_provider(self):
        transportation_provider = create_transportation_provider(
            name='Test Transportation Provider',
            service_type='Test Service Type',
            base_fare=Decimal('100.00'),
            price_per_km=Decimal('10.00'),
            contact_info='Test contact info'
        )

        url = detail_url(transportation_provider.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user to staff
        self.user.is_staff = True
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TransportationProvider.objects.filter(id=transportation_provider.id).exists())
