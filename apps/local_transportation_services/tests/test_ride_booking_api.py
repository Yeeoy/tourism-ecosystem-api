from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.local_transportation_services.models import TransportationProvider, RideBooking

RIDE_BOOKING_API_URL = reverse('local_transportation_services:ride-booking-list')


def create_user(email='user@example.com', password='password123'):
    return get_user_model().objects.create_user(email=email, password=password)


def create_ride_booking(**params):
    return RideBooking.objects.create(**params)


def detail_url(ride_booking_id):
    return reverse('local_transportation_services:ride-booking-detail', args=[ride_booking_id])


class PrivateRideBookingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

        self.transportation_provider = TransportationProvider.objects.create(
            name='Test Transportation Provider',
            service_type='Test Service Type',
            base_fare=Decimal('100.00'),
            price_per_km=Decimal('10.00'),
            contact_info='Test contact info'
        )

    def test_create_ride_booking(self):
        payload = {
            'user': self.user.id,
            'provider_id': self.transportation_provider.id,
            'pickup_location': 'Test Pickup Location',
            'drop_off_location': 'Test Drop Off Location',
            'ride_date': '2021-09-01',
            'pickup_time': '09:00:00',
            'estimated_fare': Decimal('100.00'),
            'booking_status': False
        }

        res = self.client.post(RIDE_BOOKING_API_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        ride_booking = RideBooking.objects.get(id=res.data['id'])
        for key in payload.keys():
            if key == 'user':
                self.assertEqual(payload[key], ride_booking.user.id)
            elif key == 'provider_id':
                self.assertEqual(payload[key], ride_booking.provider_id.id)
            elif key == 'ride_date':
                self.assertEqual(payload[key], str(ride_booking.ride_date))
            elif key == 'pickup_time':
                self.assertEqual(payload[key], str(ride_booking.pickup_time))
            else:
                self.assertEqual(payload[key], getattr(ride_booking, key))

    def test_retrieve_ride_bookings(self):
        create_ride_booking(
            user=self.user,
            provider_id=self.transportation_provider,
            pickup_location='Test Pickup Location',
            drop_off_location='Test Drop Off Location',
            ride_date='2021-09-01',
            pickup_time='09:00:00',
            estimated_fare=Decimal('100.00'),
            booking_status=False
        )

        create_ride_booking(
            user=self.user,
            provider_id=self.transportation_provider,
            pickup_location='Test Pickup Location 2',
            drop_off_location='Test Drop Off Location 2',
            ride_date='2021-09-02',
            pickup_time='09:00:00',
            estimated_fare=Decimal('200.00'),
            booking_status=False
        )

        res = self.client.get(RIDE_BOOKING_API_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_ride_booking_detail(self):
        ride_booking = create_ride_booking(
            user=self.user,
            provider_id=self.transportation_provider,
            pickup_location='Test Pickup Location',
            drop_off_location='Test Drop Off Location',
            ride_date='2021-09-01',
            pickup_time='09:00:00',
            estimated_fare=Decimal('100.00'),
            booking_status=False
        )

        res = self.client.get(detail_url(ride_booking.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['pickup_location'], ride_booking.pickup_location)
        self.assertEqual(res.data['drop_off_location'], ride_booking.drop_off_location)
        self.assertEqual(res.data['ride_date'], str(ride_booking.ride_date))
        self.assertEqual(res.data['pickup_time'], str(ride_booking.pickup_time))
        self.assertEqual(res.data['estimated_fare'], str(ride_booking.estimated_fare))
        self.assertEqual(res.data['booking_status'], ride_booking.booking_status)

    def test_update_ride_booking(self):
        ride_booking = create_ride_booking(
            user=self.user,
            provider_id=self.transportation_provider,
            pickup_location='Test Pickup Location',
            drop_off_location='Test Drop Off Location',
            ride_date='2021-09-01',
            pickup_time='09:00:00',
            estimated_fare=Decimal('100.00'),
            booking_status=False
        )

        payload = {
            'pickup_location': 'Updated Pickup Location',
            'drop_off_location': 'Updated Drop Off Location',
            'ride_date': '2021-09-02',
            'pickup_time': '10:00:00',
            'estimated_fare': Decimal('200.00'),
            'booking_status': True
        }

        url = detail_url(ride_booking.id)
        res = self.client.patch(url, payload)
        ride_booking.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key in payload.keys():
            if key == 'ride_date':
                self.assertEqual(payload[key], str(ride_booking.ride_date))
            elif key == 'pickup_time':
                self.assertEqual(payload[key], str(ride_booking.pickup_time))
            else:
                self.assertEqual(payload[key], getattr(ride_booking, key))

    def test_delete_ride_booking(self):
        ride_booking = create_ride_booking(
            user=self.user,
            provider_id=self.transportation_provider,
            pickup_location='Test Pickup Location',
            drop_off_location='Test Drop Off Location',
            ride_date='2021-09-01',
            pickup_time='09:00:00',
            estimated_fare=Decimal('100.00'),
            booking_status=False
        )

        url = detail_url(ride_booking.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(RideBooking.objects.filter(id=ride_booking.id).exists())
