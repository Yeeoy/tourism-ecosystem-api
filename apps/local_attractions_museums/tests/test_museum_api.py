from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.local_attractions_museums.models import Museum

# URL for the museum list
MUSEUMS_URL = reverse('local_attractions_museums:museum-list')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


# Helper function to create a museum
def create_museum(**params):
    return Museum.objects.create(**params)


def detail_url(museum_id):
    return reverse('local_attractions_museums:museum-detail', args=[museum_id])


class PublicMuseumsAPITests(TestCase):
    """Test unauthenticated museum API access"""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_museums(self):
        """Test retrieving a list of museums"""
        create_museum(
            name='Test Museum 1',
            description='Test description 1',
            location='Test Location 1',
            opening_hours='09:00',
            closing_hours='17:00',
            ticket_price=10.00
        )
        create_museum(
            name='Test Museum 2',
            description='Test description 2',
            location='Test Location 2',
            opening_hours='10:00',
            closing_hours='18:00',
            ticket_price=20.00
        )

        res = self.client.get(MUSEUMS_URL)
        print(res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_museum_detail(self):
        """Test retrieving a specific museum"""
        museum = create_museum(
            name='Test Museum',
            description='Test description',
            location='Test Location',
            opening_hours='09:00',
            closing_hours='17:00',
            ticket_price=10.00
        )

        url = detail_url(museum.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], museum.name)

    def test_create_museum_unauthorized(self):
        """Test that unauthenticated users cannot create museums"""
        payload = {
            'name': 'Test Museum',
            'description': 'Test description',
            'location': 'Test Location',
            'opening_hours': '09:00',
            'closing_hours': '17:00',
            'ticket_price': 10.00
        }
        res = self.client.post(MUSEUMS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateMuseumsAPITests(TestCase):
    """Test authenticated museum API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com',
            password='password123'
        )
        self.client.force_authenticate(self.user)

    def test_create_museum(self):
        """Test creating a new museum"""
        payload = {
            'name': 'Test Museum',
            'description': 'Test description',
            'location': 'Test Location',
            'opening_hours': '09:00',
            'closing_hours': '17:00',
            'ticket_price': 10.00
        }
        res = self.client.post(MUSEUMS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change to admin
        self.user.is_staff = True
        res = self.client.post(MUSEUMS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        museum = Museum.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(museum, key))

    def test_update_museum(self):
        """Test updating a museum"""
        museum = create_museum(
            name='Test Museum',
            description='Test description',
            location='Test Location',
            opening_hours='09:00',
            closing_hours='17:00',
            ticket_price=10.00
        )
        payload = {
            'name': 'New Name',
            'description': 'New description',
            'location': 'New Location',
            'opening_hours': '10:00',
            'closing_hours': '18:00',
            'ticket_price': 20.00
        }
        url = detail_url(museum.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change to admin
        self.user.is_staff = True
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        museum.refresh_from_db()
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(museum, key))

    def test_delete_museum(self):
        """Test deleting a museum"""
        museum = create_museum(
            name='Test Museum',
            description='Test description',
            location='Test Location',
            opening_hours='09:00',
            closing_hours='17:00',
            ticket_price=10.00
        )
        url = detail_url(museum.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Museum.objects.filter(id=museum.id).exists())

    def test_create_invalid_museum(self):
        """Test creating a museum with invalid payload"""
        payload = {
            'name': '',  # Invalid name
            'description': 'Test description',
            'location': 'Test Location',
            'opening_hours': '09:00',
            'closing_hours': '17:00',
            'ticket_price': 10.00
        }
        res = self.client.post(MUSEUMS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_museum_as_admin(self):
        """Test partial update of a museum by admin"""
        museum = create_museum(
            name='Test Museum',
            description='Test description',
            location='Test Location',
            opening_hours='09:00',
            closing_hours='17:00',
            ticket_price=10.00
        )
        self.user.is_staff = True
        self.user.save()

        payload = {'ticket_price': 20.00}
        url = detail_url(museum.id)
        res = self.client.patch(url, payload)

        museum.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(museum.ticket_price, 20.00)

    def test_delete_museum_as_admin(self):
        """Test that admin users can delete museums"""
        museum = create_museum(
            name='Test Museum',
            description='Test description',
            location='Test Location',
            opening_hours='09:00',
            closing_hours='17:00',
            ticket_price=10.00
        )
        self.user.is_staff = True
        self.user.save()

        url = detail_url(museum.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Museum.objects.filter(id=museum.id).exists())
