from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.event_organizers.models import (Event)
from apps.event_organizers.serializers import EventSerializer

EVENTS_URL = reverse('event_organizers:event-list')


def create_event(**params):
    return Event.objects.create(**params)


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def detail_url(event_id):
    return reverse('event_organizers:event-detail', args=[event_id])


class PublicEventsAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_events(self):
        create_event(
            name='Test Event 1',
            venue='Test Location 1',
            description='Test description 1',
            event_date='2021-01-01',
            start_time='09:00',
            end_time='17:00',
            entry_fee=10.00,
            max_participants=100
        )

        create_event(
            name='Test Event 2',
            venue='Test Location 2',
            description='Test description 2',
            event_date='2021-02-01',
            start_time='10:00',
            end_time='18:00',
            entry_fee=20.00,
            max_participants=200
        )

        res = self.client.get(EVENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_event_detail(self):
        event = create_event(
            name='Test Event',
            venue='Test Location',
            description='Test description',
            event_date='2021-03-01',
            start_time='09:00:00',
            end_time='17:00:00',
            entry_fee=30.00,
            max_participants=300
        )

        res = self.client.get(detail_url(event.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        expected_data = EventSerializer(event).data
        self.assertEqual(res.data, expected_data)


class PrivateEventsAPITests(TestCase):

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_event(self):
        payload = {
            'name': 'Test Event',
            'venue': 'Test Location',
            'description': 'Test description',
            'event_date': '2021-04-01',
            'start_time': '09:00:00',
            'end_time': '17:00:00',
            'entry_fee': 40.00,
            'max_participants': 400
        }

        res = self.client.post(EVENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change to admin user
        self.user.is_staff = True
        res = self.client.post(EVENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        event = Event.objects.get(id=res.data['id'])
        for key in payload.keys():
            if key == 'event_date':
                # Convert string date to datetime.date object for comparison
                self.assertEqual(
                    datetime.strptime(payload[key], '%Y-%m-%d').date(),
                    getattr(event, key)
                )
            elif key in ['start_time', 'end_time']:
                # Convert string time to datetime.time object for comparison
                self.assertEqual(
                    datetime.strptime(payload[key], '%H:%M:%S').time(),
                    getattr(event, key)
                )
            else:
                self.assertEqual(payload[key], getattr(event, key))

    def test_update_event(self):
        event = create_event(
            name='Old Name',
            venue='Test Location',
            description='Test description',
            event_date='2021-05-01',
            start_time='09:00:00',
            end_time='17:00:00',
            entry_fee=50.00,
            max_participants=500
        )

        payload = {
            'name': 'New Name',
            'venue': 'New Location',
            'description': 'New description',
            'event_date': '2021-06-01',
            'start_time': '10:00:00',
            'end_time': '18:00:00',
            'entry_fee': 60.00,
            'max_participants': 600
        }

        res = self.client.patch(detail_url(event.id), payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change to admin user
        self.user.is_staff = True
        res = self.client.patch(detail_url(event.id), payload)

        event.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key in payload.keys():
            if key == 'event_date':
                # Convert string date to datetime.date object for comparison
                self.assertEqual(
                    datetime.strptime(payload[key], '%Y-%m-%d').date(),
                    getattr(event, key)
                )
            elif key in ['start_time', 'end_time']:
                # Convert string time to datetime.time object for comparison
                self.assertEqual(
                    datetime.strptime(payload[key], '%H:%M:%S').time(),
                    getattr(event, key)
                )
            else:
                self.assertEqual(payload[key], getattr(event, key))

    def test_partial_update_event(self):
        event = create_event(
            name='Old Name',
            venue='Test Location',
            description='Test description',
            event_date='2021-07-01',
            start_time='09:00:00',
            end_time='17:00:00',
            entry_fee=70.00,
            max_participants=700
        )

        payload = {
            'name': 'New Name',
        }

        res = self.client.patch(detail_url(event.id), payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change to admin user
        self.user.is_staff = True
        res = self.client.patch(detail_url(event.id), payload)

        event.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(payload['name'], event.name)

    def test_delete_event(self):
        event = create_event(
            name='Test Event',
            venue='Test Location',
            description='Test description',
            event_date='2021-08-01',
            start_time='09:00:00',
            end_time='17:00:00',
            entry_fee=80.00,
            max_participants=800
        )

        res = self.client.delete(detail_url(event.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change to admin user
        self.user.is_staff = True
        res = self.client.delete(detail_url(event.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Event.objects.filter(id=event.id).exists())
