from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.local_attractions_museums.models import Attraction

ATTRACTIONS_URL = reverse('local_attractions_museums:attraction-list')
MUSEUMS_URL = reverse('local_attractions_museums:museum-list')
TICKETS_URL = reverse('local_attractions_museums:ticket-list')

BOOKINGS_URL = reverse('local_attractions_museums:booking-list')
EDUCATION_CONTENT_URL = (
    reverse('local_attractions_museums:education-contents-list'))
TOUR_GUIDES_URL = reverse('local_attractions_museums:tour-guides-list')


def create_user(email='user@example.com', password='pass123'):
    return get_user_model().objects.create_user(email=email, password=password)


def create_superuser(email='superuser@example.com', password='root123'):
    return get_user_model().objects.create_superuser(
        email=email, password=password
    )


def detail_url(model_name, obj_id):
    return reverse(f'local_attractions_museums:'
                   f'{model_name}-detail', args=[obj_id])


class PublicAttractionsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_not_login_required(self):
        res = self.client.get(ATTRACTIONS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_attractions(self):
        Attraction.objects.create(name='Great Wall of China',
                                  description='A great wall',
                                  location='China', opening_hours='8:00',
                                  closing_hours='18:00', ticket_price=100.00)
        Attraction.objects.create(name='Eiffel Tower',
                                  description='A tower',
                                  location='France', opening_hours='8:00',
                                  closing_hours='18:00', ticket_price=100.00)
        res = self.client.get(ATTRACTIONS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

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


class PrivateAttractionsApiTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
