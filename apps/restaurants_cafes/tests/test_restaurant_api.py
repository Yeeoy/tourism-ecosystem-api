from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.event_organizers.tests.test_promotion_api import create_user
from apps.restaurants_cafes.models import Restaurant

RESTAURANT_API_URL = reverse('restaurants_cafes:restaurant-list')


def create_restaurant(**params):
    return Restaurant.objects.create(**params)


def detail_url(restaurant_id):
    return reverse('restaurants_cafes:restaurant-detail', args=[restaurant_id])


class PublicRestaurantApiTests(TestCase):
    """Test the publicly available restaurants API"""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_restaurants(self):
        """Test retrieving a list of restaurants"""
        create_restaurant(
            name='KFC',
            location='Kampala',
            cuisine_type='Fast Food',
            opening_hours='8:00AM - 10:00PM',
            contact_info='0700000000'
        )

        create_restaurant(
            name='Cafe Javas',
            location='Kampala',
            cuisine_type='Fast Food',
            opening_hours='8:00AM - 10:00PM',
            contact_info='0700000000'
        )

        res = self.client.get(RESTAURANT_API_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data[0]['name'], 'KFC')
        self.assertEqual(res.data[1]['name'], 'Cafe Javas')

    def test_retrieve_restaurant_detail(self):
        """Test retrieving a restaurant detail"""
        restaurant = create_restaurant(
            name='KFC',
            location='Kampala',
            cuisine_type='Fast Food',
            opening_hours='8:00AM - 10:00PM',
            contact_info='0700000000'
        )

        url = detail_url(restaurant.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], restaurant.name)
        self.assertEqual(res.data['location'], restaurant.location)
        self.assertEqual(res.data['cuisine_type'], restaurant.cuisine_type)
        self.assertEqual(res.data['opening_hours'], restaurant.opening_hours)
        self.assertEqual(res.data['contact_info'], restaurant.contact_info)


class PrivateRestaurantApiTests(TestCase):
    """Test the authorized user restaurants API"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example',
            password='test1234'
        )
        self.client.force_authenticate(self.user)

    def test_create_restaurant_successful(self):
        """Test creating a new restaurant"""
        payload = {
            'name': 'KFC',
            'location': 'Kampala',
            'cuisine_type': 'Fast Food',
            'opening_hours': '8:00AM - 10:00PM',
            'contact_info': '0700000000'
        }

        res = self.client.post(RESTAURANT_API_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user to staff
        self.user.is_staff = True
        res = self.client.post(RESTAURANT_API_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        restaurant = Restaurant.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(restaurant, key))

    def test_update_restaurant_successful(self):
        """Test updating a restaurant"""
        restaurant = create_restaurant(
            name='KFC',
            location='Kampala',
            cuisine_type='Fast Food',
            opening_hours='8:00AM - 10:00PM',
            contact_info='0700000000'
        )

        payload = {
            'name': 'KFC',
            'location': 'Kampala',
            'cuisine_type': 'Fast Food',
            'opening_hours': '8:00AM - 10:00PM',
            'contact_info': '0700000000'
        }

        url = detail_url(restaurant.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        restaurant.refresh_from_db()
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(restaurant, key))

    def test_delete_restaurant_successful(self):
        """Test deleting a restaurant"""
        restaurant = create_restaurant(
            name='KFC',
            location='Kampala',
            cuisine_type='Fast Food',
            opening_hours='8:00AM - 10:00PM',
            contact_info='0700000000'
        )

        url = detail_url(restaurant.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Restaurant.objects.filter(id=restaurant.id).exists())
