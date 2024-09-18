from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.restaurants_cafes.models import OnlineOrder, Restaurant

ONLINE_ORDER_URL = reverse('restaurants_cafes:online-order-list')


def create_user(email='test@example.com', password='test1234'):
    return get_user_model().objects.create_user(email=email, password=password)


def create_online_order(**params):
    return OnlineOrder.objects.create(**params)


def detail_url(online_order_id):
    return reverse('restaurants_cafes:online-order-detail', args=[online_order_id])


class PrivateOnlineOrderApiTests(TestCase):
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

    def test_create_online_order(self):
        """Test creating an online order"""
        payload = {
            'restaurant': self.restaurant.id,
            'user': self.user.id,
            'order_date': '2021-09-01',
            'order_time': '12:00:00',
            'total_amount': Decimal('100.00'),
            'order_status': 'Pending'
        }
        res = self.client.post(ONLINE_ORDER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['restaurant'], self.restaurant.id)
        self.assertEqual(res.data['user'], self.user.id)
        self.assertEqual(res.data['order_date'], payload['order_date'])
        self.assertEqual(res.data['order_time'], payload['order_time'])
        self.assertEqual(res.data['order_status'], payload['order_status'])

    def test_retrieve_online_orders(self):
        user2 = create_user(email="user2@example.com", password="test1234")

        """Test retrieving a list of online orders"""
        create_online_order(
            restaurant=self.restaurant,
            user=user2,
            order_date='2021-09-01',
            order_time='12:00:00',
            total_amount=Decimal('100.00'),
            order_status='Pending'
        )

        create_online_order(
            restaurant=self.restaurant,
            user=self.user,
            order_date='2021-09-01',
            order_time='12:00:00',
            total_amount=Decimal('100.00'),
            order_status='Pending'
        )

        res = self.client.get(ONLINE_ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['restaurant'], self.restaurant.id)
        self.assertEqual(res.data[0]['user'], self.user.id)
        self.assertEqual(res.data[0]['order_date'], '2021-09-01')
        self.assertEqual(res.data[0]['order_time'], '12:00:00')
        self.assertEqual(res.data[0]['total_amount'], '100.00')
        self.assertEqual(res.data[0]['order_status'], 'Pending')

    def test_update_online_order(self):
        user2 = create_user(email="user2@example.com", password="test1234")

        """Test updating an online order"""

        online_order = create_online_order(
            restaurant=self.restaurant,
            user=user2,
            order_date='2021-09-01',
            order_time='12:00:00',
            total_amount=Decimal('100.00'),
            order_status='Pending'
        )

        online_order2 = create_online_order(
            restaurant=self.restaurant,
            user=self.user,
            order_date='2021-09-01',
            order_time='12:00:00',
            total_amount=Decimal('100.00'),
            order_status='Pending'
        )

        payload = {
            'restaurant': self.restaurant.id,
            'user': self.user.id,
            'order_date': '2021-09-01',
            'order_time': '12:00:00',
            'total_amount': Decimal('100.00'),
            'order_status': 'Completed'
        }

        url = detail_url(online_order.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        url = detail_url(online_order2.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['order_status'], 'Completed')

    def test_delete_online_order(self):
        online_order = create_online_order(
            restaurant=self.restaurant,
            user=self.user,
            order_date='2021-09-01',
            order_time='12:00:00',
            total_amount=Decimal('100.00'),
            order_status='Pending'
        )

        url = detail_url(online_order.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(OnlineOrder.objects.count(), 0)
