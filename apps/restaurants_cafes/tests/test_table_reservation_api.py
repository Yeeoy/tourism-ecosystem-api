from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.restaurants_cafes.models import TableReservation, Restaurant

TABLE_RESERVATION_URL = reverse('restaurants_cafes:table-reservation-list')


def create_user(email='test@example.com', password='test1234'):
    return get_user_model().objects.create_user(email=email, password=password)


def create_table_reservation(**params):
    return TableReservation.objects.create(**params)


def detail_url(table_reservation_id):
    return reverse('restaurants_cafes:table-reservation-detail', args=[table_reservation_id])


class PrivateTableReservationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
        self.restaurant = Restaurant.objects.create(
            name='KFC',
            location='Kampala',
            cuisine_type='Fast Food',
            opening_hours='8:00AM - 10:00PM',
            contact_info='0700000000'
        )

    def test_create_table_reservation(self):
        """Test creating a table reservation"""
        payload = {
            'restaurant': self.restaurant.id,
            'user': self.user.id,
            'reservation_date': '2021-09-01',
            'reservation_time': '12:00:00',
            'number_of_guests': 4,
            'reservation_status': 'Pending'
        }
        res = self.client.post(TABLE_RESERVATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['restaurant'], self.restaurant.id)
        self.assertEqual(res.data['user'], self.user.id)
        self.assertEqual(res.data['reservation_date'], payload['reservation_date'])
        self.assertEqual(res.data['reservation_time'], payload['reservation_time'])
        self.assertEqual(res.data['number_of_guests'], payload['number_of_guests'])
        self.assertEqual(res.data['reservation_status'], payload['reservation_status'])

    def test_retrieve_table_reservations(self):
        user2 = create_user(email="user2@example.com", password="test1234")
        """Test retrieving a list of table reservations"""
        create_table_reservation(
            restaurant=self.restaurant,
            user=user2,
            reservation_date='2021-09-01',
            reservation_time='12:00:00',
            number_of_guests=4,
            reservation_status='Pending'
        )

        create_table_reservation(
            restaurant=self.restaurant,
            user=self.user,
            reservation_date='2021-09-11',
            reservation_time='18:00:00',
            number_of_guests=7,
            reservation_status='Completed'
        )

        res = self.client.get(TABLE_RESERVATION_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_update_table_reservation(self):
        user2 = create_user(email="test2@example.com", password="test1234")

        """Test updating a table reservation"""
        table_reservation = create_table_reservation(
            restaurant=self.restaurant,
            user=user2,
            reservation_date='2021-09-01',
            reservation_time='12:00:00',
            number_of_guests=4,
            reservation_status='Pending'
        )

        table_reservation2 = create_table_reservation(
            restaurant=self.restaurant,
            user=self.user,
            reservation_date='2021-09-11',
            reservation_time='18:00:00',
            number_of_guests=7,
            reservation_status='Completed'
        )

        payload = {
            'restaurant': self.restaurant.id,
            'user': self.user.id,
            'reservation_date': '2021-09-18',
            'reservation_time': '20:00:00',
            'number_of_guests': 8,
            'reservation_status': 'Confirmed'
        }

        url = detail_url(table_reservation.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        res = self.client.patch(detail_url(table_reservation2.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        table_reservation2.refresh_from_db()
        self.assertEqual(res.data['reservation_date'], '2021-09-18')
        self.assertEqual(res.data['reservation_time'], '20:00:00')
        self.assertEqual(table_reservation2.number_of_guests, 8)
        self.assertEqual(table_reservation2.reservation_status, 'Confirmed')

    def test_delete_table_reservation(self):
        """Test deleting a table reservation"""
        table_reservation = create_table_reservation(
            restaurant=self.restaurant,
            user=self.user,
            reservation_date='2021-09-01',
            reservation_time='12:00:00',
            number_of_guests=4,
            reservation_status='Pending'
        )

        res = self.client.delete(detail_url(table_reservation.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TableReservation.objects.filter(id=table_reservation.id).exists())
