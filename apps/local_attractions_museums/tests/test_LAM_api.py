from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.local_attractions_museums.models import (Attraction, Museum, Ticket,
                                                   TourGuide, Booking)

ATTRACTIONS_URL = reverse('local_attractions_museums:attraction-list')
MUSEUMS_URL = reverse('local_attractions_museums:museum-list')
TICKETS_URL = reverse('local_attractions_museums:ticket-list')
TOURGUIDES_URL = reverse('local_attractions_museums:tourguide-list')
BOOKINGS_URL = reverse('local_attractions_museums:booking-list')
EDUCATION_CONTENT_URL = (
    reverse('local_attractions_museums:education content-list'))


def create_user(email='user@example.com', password='testpass123'):
    return get_user_model().objects.create_user(email=email, password=password)


def detail_url(model_name, obj_id):
    return reverse(f'local_attractions_museums:'
                   f'{model_name}-detail', args=[obj_id])


# Test for Attraction API
class PublicAttractionApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_attractions(self):
        res = self.client.get(ATTRACTIONS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)


class PrivateAttractionApiTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_attraction(self):
        payload = {
            'name': 'Grand Canyon',
            'description': 'A famous canyon',
            'location': 'Arizona',
            'opening_hours': '06:00',
            'closing_hours': '18:00',
            'ticket_price': '50.00'
        }
        res = self.client.post(ATTRACTIONS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_attraction(self):
        attraction = Attraction.objects.create(
            name='Statue of Liberty',
            description='Famous statue in NYC',
            location='New York',
            opening_hours='09:00',
            closing_hours='17:00',
            ticket_price='20.00'
        )
        payload = {'name': 'Liberty Island'}
        url = detail_url('attraction', attraction.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        attraction.refresh_from_db()
        self.assertEqual(attraction.name, payload['name'])

    def test_delete_attraction(self):
        attraction = Attraction.objects.create(
            name='Eiffel Tower',
            description='Iconic tower in Paris',
            location='Paris',
            opening_hours='10:00',
            closing_hours='22:00',
            ticket_price='25.00'
        )
        url = detail_url('attraction', attraction.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        attractions = Attraction.objects.filter(id=attraction.id)
        self.assertFalse(attractions.exists())


# Test for Museum API
class PublicMuseumApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_museums(self):
        res = self.client.get(MUSEUMS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)


class PrivateMuseumApiTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_museum(self):
        payload = {
            'name': 'Louvre Museum',
            'description': 'Famous museum in Paris',
            'location': 'Paris',
            'opening_hours': '09:00',
            'closing_hours': '18:00',
            'ticket_price': '15.00'
        }
        res = self.client.post(MUSEUMS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_museum(self):
        museum = Museum.objects.create(
            name='Metropolitan Museum of Art',
            description='A major museum in NYC',
            location='New York',
            opening_hours='09:00',
            closing_hours='17:30',
            ticket_price='25.00'
        )
        payload = {'name': 'The Met'}
        url = detail_url('museum', museum.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        museum.refresh_from_db()
        self.assertEqual(museum.name, payload['name'])

    def test_delete_museum(self):
        museum = Museum.objects.create(
            name='British Museum',
            description='A major museum in London',
            location='London',
            opening_hours='10:00',
            closing_hours='17:00',
            ticket_price='Free'
        )
        url = detail_url('museum', museum.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        museums = Museum.objects.filter(id=museum.id)
        self.assertFalse(museums.exists())


# Test for Booking API
class BookingApiTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.attraction = Attraction.objects.create(
            name='Grand Canyon',
            description='A famous canyon',
            location='Arizona',
            opening_hours='06:00',
            closing_hours='18:00',
            ticket_price='50.00'
        )
        self.ticket = Ticket.objects.create(
            attraction=self.attraction,
            price='50.00',
            purchase_date='2024-08-08T14:00:00Z',
            valid_until='2024-08-15T14:00:00Z'
        )
        self.tour_guide = TourGuide.objects.create(
            name='John Doe',
            bio='Experienced tour guide',
            available_from='09:00',
            available_to='17:00',
            languages='English'
        )

    def test_create_booking(self):
        payload = {
            'user': self.user.id,
            'ticket': self.ticket.id,
            'guide': self.tour_guide.id,
            'visit_date': '2024-09-15T10:00:00Z'
        }
        res = self.client.post(BOOKINGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_booking_limited_to_user(self):
        user2 = create_user(email='user2@example.com')
        booking = Booking.objects.create(
            user=self.user,
            ticket=self.ticket,
            guide=self.tour_guide,
            visit_date='2024-09-15T10:00:00Z'
        )
        self.client.force_authenticate(user2)
        url = detail_url('booking', booking.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
