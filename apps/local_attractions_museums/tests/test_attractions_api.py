from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.local_attractions_museums.models import Attraction

# URL for the attractions list
ATTRACTIONS_URL = reverse('local_attractions_museums:attraction-list')


# Helper function to create an attraction
def create_attraction(**params):
    return Attraction.objects.create(**params)


# Helper function to create a user
def create_user(**params):
    return get_user_model().objects.create_user(**params)


# Helper function to get detail URL for a specific attraction
def detail_url(attraction_id):
    return reverse('local_attractions_museums:attraction-detail',
                   args=[attraction_id])


class PublicAttractionsAPITests(TestCase):
    """Test unauthenticated attraction API access"""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_attractions(self):
        """Test retrieving a list of attractions"""
        create_attraction(
            name='Test Attraction 1',
            description='Test description 1',
            location='Test Location 1',
            opening_hours='09:00',
            closing_hours='17:00',
            ticket_price=10.00
        )
        create_attraction(
            name='Test Attraction 2',
            description='Test description 2',
            location='Test Location 2',
            opening_hours='10:00',
            closing_hours='18:00',
            ticket_price=20.00
        )

        res = self.client.get(ATTRACTIONS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_attraction_detail(self):
        """Test retrieving a specific attraction"""
        attraction = create_attraction(
            name='Test Attraction',
            description='Test description',
            location='Test Location',
            opening_hours='09:00',
            closing_hours='17:00',
            ticket_price=10.00
        )

        url = detail_url(attraction.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], attraction.name)

    def test_create_attraction_unauthorized(self):
        """Test that unauthenticated users cannot create attractions"""
        payload = {
            'name': 'Test Attraction',
            'description': 'Test description',
            'location': 'Test Location',
            'opening_hours': '09:00',
            'closing_hours': '17:00',
            'ticket_price': 10.00
        }
        res = self.client.post(ATTRACTIONS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAttractionsAPITests(TestCase):
    """Test authenticated users attraction API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com',
            password='password123'
        )
        self.client.force_authenticate(self.user)

    def test_create_attraction_as_non_admin(self):
        """Test that non-admin users cannot create attractions"""
        payload = {
            'name': 'Test Attraction',
            'description': 'Test description',
            'location': 'Test Location',
            'opening_hours': '09:00',
            'closing_hours': '17:00',
            'ticket_price': 10.00
        }
        res = self.client.post(ATTRACTIONS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_attraction_as_admin(self):
        """Test that admin users can create attractions"""
        self.user.is_staff = True  # Set the user as admin
        self.user.save()

        payload = {
            'name': 'Test Attraction',
            'description': 'Test description',
            'location': 'Test Location',
            'opening_hours': '09:00',
            'closing_hours': '17:00',
            'ticket_price': 10.00
        }
        res = self.client.post(ATTRACTIONS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['name'], payload['name'])

    def test_update_attraction_as_admin(self):
        """Test that admin users can update attractions"""
        attraction = create_attraction(
            name='Old Name',
            description='Test description',
            location='Test Location',
            opening_hours='09:00',
            closing_hours='17:00',
            ticket_price=10.00
        )
        self.user.is_staff = True
        self.user.save()

        payload = {'name': 'New Name'}
        url = detail_url(attraction.id)
        res = self.client.patch(url, payload)

        attraction.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(attraction.name, 'New Name')

    def test_partial_update_attraction_as_admin(self):
        """Test partial update of an attraction by admin"""
        attraction = create_attraction(
            name='Test Attraction',
            description='Test description',
            location='Test Location',
            opening_hours='09:00',
            closing_hours='17:00',
            ticket_price=10.00
        )
        self.user.is_staff = True
        self.user.save()

        payload = {'ticket_price': 20.00}
        url = detail_url(attraction.id)
        res = self.client.patch(url, payload)

        attraction.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(attraction.ticket_price, 20.00)

    def test_delete_attraction_as_admin(self):
        """Test that admin users can delete attractions"""
        attraction = create_attraction(
            name='Test Attraction',
            description='Test description',
            location='Test Location',
            opening_hours='09:00',
            closing_hours='17:00',
            ticket_price=10.00
        )
        self.user.is_staff = True
        self.user.save()

        url = detail_url(attraction.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Attraction.objects.filter(id=attraction.id).exists())

    def test_create_invalid_attraction(self):
        """Test creating an attraction with invalid payload"""
        self.user.is_staff = True
        self.user.save()

        payload = {
            'name': '',  # Invalid name
            'description': 'Test description',
            'location': 'Test Location',
            'opening_hours': '09:00',
            'closing_hours': '17:00',
            'ticket_price': 10.00
        }
        res = self.client.post(ATTRACTIONS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
