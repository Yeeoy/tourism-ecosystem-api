from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.tourism_information_center.models import Destination

DESTINATION_URL_API = reverse('tourism_information_center:destination-list')


def create_user(email='test@example.com', password='test1234'):
    return get_user_model().objects.create_user(email=email, password=password)


def create_destination(**params):
    return Destination.objects.create(**params)


def detail_url(destination_id):
    return reverse('tourism_information_center:destination-detail', args=[destination_id])


class PublicDestinationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_retrieve_destinations(self):
        """Test retrieving a list of destinations"""
        create_destination(
            name='Kampala',
            category='City',
            description='The capital city of Uganda',
            location='Central Region',
            opening_hours='8:00AM - 5:00PM',
            contact_info='0700000000'
        )

        create_destination(
            name='Murchison Falls National Park',
            category='National Park',
            description='The largest national park in Uganda',
            location='Northern Region',
            opening_hours='6:00AM - 6:00PM',
            contact_info='0700000000'
        )

        res = self.client.get(DESTINATION_URL_API)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data[0]['name'], 'Kampala')
        self.assertEqual(res.data[1]['name'], 'Murchison Falls National Park')

    def test_retrieve_destination_detail(self):
        """Test retrieving a destination detail"""
        destination = create_destination(
            name='Kampala',
            category='City',
            description='The capital city of Uganda',
            location='Central Region',
            opening_hours='8:00AM - 5:00PM',
            contact_info='0700000000'
        )

        res = self.client.get(detail_url(destination.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], destination.name)
        self.assertEqual(res.data['category'], destination.category)
        self.assertEqual(res.data['description'], destination.description)
        self.assertEqual(res.data['location'], destination.location)
        self.assertEqual(res.data['opening_hours'], destination.opening_hours)
        self.assertEqual(res.data['contact_info'], destination.contact_info)


class PrivateDestinationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_create_destination(self):
        """Test creating a destination"""
        payload = {
            'name': 'Kampala',
            'category': 'City',
            'description': 'The capital city of Uganda',
            'location': 'Central Region',
            'opening_hours': '8:00AM - 5:00PM',
            'contact_info': '0700000000'
        }

        res = self.client.post(DESTINATION_URL_API, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user to admin
        self.user.is_staff = True

        res = self.client.post(DESTINATION_URL_API, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        destination = Destination.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(destination, key))

    def test_update_destination(self):
        """Test updating a destination"""
        destination = create_destination(
            name='Kampala',
            category='City',
            description='The capital city of Uganda',
            location='Central Region',
            opening_hours='8:00AM - 5:00PM',
            contact_info='0700000000'
        )

        payload = {
            'name': 'Murchison Falls National Park',
            'category': 'National Park',
            'description': 'The largest national park in Uganda',
            'location': 'Northern Region',
            'opening_hours': '6:00AM - 6:00PM',
            'contact_info': '0700000000'
        }

        url = detail_url(destination.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user to admin
        self.user.is_staff = True
        res = self.client.patch(url, payload)

        destination.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(destination, key))

    def test_delete_destination(self):
        """Test deleting a destination"""
        destination = create_destination(
            name='Kampala',
            category='City',
            description='The capital city of Uganda',
            location='Central Region',
            opening_hours='8:00AM - 5:00PM',
            contact_info='0700000000'
        )

        url = detail_url(destination.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user to admin
        self.user.is_staff = True
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Destination.objects.filter(id=destination.id).exists())

    def test_create_destination_invalid(self):
        """Test creating a destination with invalid payload"""
        payload = {
            'name': '',
            'category': 'City',
            'description': 'The capital city of Uganda',
            'location': 'Central Region',
            'opening_hours': '8:00AM - 5:00PM',
            'contact_info': '0700000000'
        }

        res = self.client.post(DESTINATION_URL_API, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user to admin
        self.user.is_staff = True
        res = self.client.post(DESTINATION_URL_API, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
