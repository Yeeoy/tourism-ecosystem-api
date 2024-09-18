from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.restaurants_cafes.models import Menu, Restaurant

MENU_API_URL = reverse('restaurants_cafes:menu-list')


def create_user(email='test@example.com', password='test1234'):
    return get_user_model().objects.create_user(email=email, password=password)


def create_menu(**params):
    return Menu.objects.create(**params)


def detail_url(menu_id):
    return reverse('restaurants_cafes:menu-detail', args=[menu_id])


class PublicMenuApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.restaurant = Restaurant.objects.create(
            name='KFC',
            location='Kampala',
            cuisine_type='Fast Food',
            opening_hours='8:00AM - 10:00PM',
            contact_info='0700000000'
        )

    def test_retrieve_menus(self):
        """Test retrieving a list of menus"""
        create_menu(
            restaurant=self.restaurant,
            item_name='Chicken',
            description='Fried Chicken',
            price=Decimal('10000')
        )

        create_menu(
            restaurant=self.restaurant,
            item_name='Chips',
            description='French Fries',
            price=Decimal('5000')
        )

        res = self.client.get(MENU_API_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data[0]['item_name'], 'Chicken')
        self.assertEqual(res.data[1]['item_name'], 'Chips')

    def test_retrieve_menu_detail(self):
        """Test retrieving a menu detail"""
        menu = create_menu(
            restaurant=self.restaurant,
            item_name='Chicken',
            description='Fried Chicken',
            price=Decimal('10000')
        )

        url = detail_url(menu.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['item_name'], menu.item_name)
        self.assertEqual(res.data['description'], menu.description)
        self.assertEqual(res.data['price'], '10000.00')


class PrivateMenuApiTests(TestCase):
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

    def test_create_menu(self):
        """Test creating a new menu"""
        payload = {
            'restaurant': self.restaurant.id,
            'item_name': 'Chicken',
            'description': 'Fried Chicken',
            'price': Decimal('10000')
        }
        res = self.client.post(MENU_API_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user to admin
        self.user.is_staff = True
        res = self.client.post(MENU_API_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        menu = Menu.objects.get(id=res.data['id'])
        self.assertEqual(menu.item_name, payload['item_name'])
        self.assertEqual(menu.description, payload['description'])
        self.assertEqual(menu.price, payload['price'])

    def test_update_menu(self):
        """Test updating a menu"""
        menu = create_menu(
            restaurant=self.restaurant,
            item_name='Chicken',
            description='Fried Chicken',
            price=Decimal('10000')
        )

        payload = {
            'item_name': 'Chips',
            'description': 'French Fries',
            'price': Decimal('5000')
        }

        url = detail_url(menu.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user to admin
        self.user.is_staff = True
        self.client.patch(url, payload)

        menu.refresh_from_db()
        self.assertEqual(menu.item_name, payload['item_name'])
        self.assertEqual(menu.description, payload['description'])
        self.assertEqual(menu.price, payload['price'])

    def test_delete_menu(self):
        """Test deleting a menu"""
        menu = create_menu(
            restaurant=self.restaurant,
            item_name='Chicken',
            description='Fried Chicken',
            price=Decimal('10000')
        )

        url = detail_url(menu.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user to admin
        self.user.is_staff = True
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Menu.objects.filter(id=menu.id).exists())
