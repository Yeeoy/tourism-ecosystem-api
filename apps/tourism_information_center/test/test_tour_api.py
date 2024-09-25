from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.tourism_information_center.models import Tour, Destination

TOUR_API = reverse('tourism_information_center:tour-list')


def create_user(email='test@example.com', password='test1234'):
    return get_user_model().objects.create_user(email=email, password=password)


def create_tour(**params):
    return Tour.objects.create(**params)


def detail_url(tour_id):
    return reverse('tourism_information_center:tour-detail', args=[tour_id])


class PublicTourApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.destination = Destination.objects.create(
            name='Kampala',
            category='City',
            description='The capital city of Uganda',
            location='Central Region',
            opening_hours='8:00AM - 5:00PM',
            contact_info='0700000000'
        )

    def test_retrieve_tours(self):
        """Test retrieving a list of tours"""
        create_tour(
            destination=self.destination,
            name='Kampala City Tour',
            tour_type='City Tour',
            duration='4 hours',
            price_per_person=Decimal('50000'),
            max_capacity=10,
            tour_date='2022-01-01',
            guide_name='John Doe',
        )

        create_tour(
            destination=self.destination,
            name='Kampala Night Tour',
            tour_type='City Tour',
            duration='2 hours',
            price_per_person=Decimal('30000'),
            max_capacity=5,
            tour_date='2022-02-01',
            guide_name='Jane Doe',
        )

        res = self.client.get(TOUR_API)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data[0]['name'], 'Kampala City Tour')
        self.assertEqual(res.data[1]['name'], 'Kampala Night Tour')

    def test_retrieve_tour_detail(self):
        """Test retrieving a tour detail"""
        tour = create_tour(
            destination=self.destination,
            name='Kampala City Tour',
            tour_type='City Tour',
            duration='4 hours',
            price_per_person=Decimal('50000'),
            max_capacity=10,
            tour_date='2022-01-01',
            guide_name='John Doe',
        )

        url = detail_url(tour.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], 'Kampala City Tour')
        self.assertEqual(res.data['tour_type'], 'City Tour')
        self.assertEqual(res.data['duration'], '4 hours')
        self.assertEqual(res.data['price_per_person'], '50000.00')
        self.assertEqual(res.data['max_capacity'], 10)
        self.assertEqual(res.data['tour_date'], '2022-01-01')
        self.assertEqual(res.data['guide_name'], 'John Doe')


class PrivateTourApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
        self.destination = Destination.objects.create(
            name='Kampala',
            category='City',
            description='The capital city of Uganda',
            location='Central Region',
            opening_hours='8:00AM - 5:00PM',
            contact_info='0700000000'
        )

    def test_create_tour(self):
        """Test creating a tour"""
        payload = {
            'destination': self.destination.id,
            'name': 'Kampala City Tour',
            'tour_type': 'City Tour',
            'duration': '4 hours',
            'price_per_person': '50000.00',
            'max_capacity': 10,
            'tour_date': '2022-01-01',
            'guide_name': 'John Doe',
        }
        res = self.client.post(TOUR_API, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user to admin
        self.user.is_staff = True
        res = self.client.post(TOUR_API, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tour = Tour.objects.get(id=res.data['id'])
        for key in payload.keys():
            if key == 'destination':
                self.assertEqual(payload['destination'], tour.destination.id)  # 比较 destination 的 ID
            elif key == 'max_capacity':
                self.assertEqual(payload[key], getattr(tour, key))
            else:
                self.assertEqual(payload[key], str(getattr(tour, key)))

    def test_update_tour(self):
        """Test updating a tour"""
        tour = create_tour(
            destination=self.destination,
            name='Kampala City Tour',
            duration='4 hours',
            price_per_person=Decimal('50000'),
            max_capacity=10,
            tour_date='2022-01-01',
            guide_name='John Doe',
        )
        payload = {
            'name': 'Kampala Night Tour',
            'duration': '2 hours',
            'price_per_person': '30000.00',
            'max_capacity': 5,
            'tour_date': '2022-02-01',
            'guide_name': 'Jane Doe',
        }
        url = detail_url(tour.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user to admin
        self.user.is_staff = True
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tour.refresh_from_db()
        for key in payload.keys():
            if key == 'destination':
                self.assertEqual(payload['destination'], tour.destination.id)  # 比较 destination 的 ID
            elif key == 'max_capacity':
                self.assertEqual(payload[key], getattr(tour, key))
            else:
                self.assertEqual(payload[key], str(getattr(tour, key)))

    def test_delete_tour(self):
        """Test deleting a tour"""
        tour = create_tour(
            destination=self.destination,
            name='Kampala City Tour',
            duration='4 hours',
            price_per_person=Decimal('50000'),
            max_capacity=10,
            tour_date='2022-01-01',
            guide_name='John Doe',
        )
        url = detail_url(tour.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user to admin
        self.user.is_staff = True
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tour.objects.filter(id=tour.id).exists())
