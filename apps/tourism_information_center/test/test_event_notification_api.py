from datetime import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.tourism_information_center.models import EventNotification

EVENT_NOTIFICATION_URL_API = reverse('tourism_information_center:event-notification-list')


def create_user(email='test@example.com', password='test1234'):
    return get_user_model().objects.create_user(email=email, password=password)


def create_event_notification(**params):
    return EventNotification.objects.create(**params)


def detail_url(event_notification_id):
    return reverse('tourism_information_center:event-notification-detail', args=[event_notification_id])


class PublicEventNotificationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_retrieve_event_notifications(self):
        """Test retrieving a list of event notifications"""
        create_event_notification(
            title='Uganda Tourism Board',
            description='UTB is organizing a tourism expo',
            event_date='2022-01-01',
            location='Kampala',
            entry_fee=Decimal('10000'),
            target_audience='Tourists'
        )

        create_event_notification(
            title='Uganda Wildlife Authority',
            description='UWA is organizing a wildlife conservation event',
            event_date='2022-02-01',
            location='Murchison Falls National Park',
            entry_fee=Decimal('20000'),
            target_audience='Conservationists'
        )

        res = self.client.get(EVENT_NOTIFICATION_URL_API)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data[0]['title'], 'Uganda Tourism Board')
        self.assertEqual(res.data[1]['title'], 'Uganda Wildlife Authority')

    def test_retrieve_event_notification_detail(self):
        """Test retrieving an event notification detail"""
        event_notification = create_event_notification(
            title='Uganda Tourism Board',
            description='UTB is organizing a tourism expo',
            event_date='2022-01-01',
            location='Kampala',
            entry_fee=Decimal('10000'),
            target_audience='Tourists'
        )

        url = detail_url(event_notification.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], event_notification.title)
        self.assertEqual(res.data['description'], event_notification.description)
        self.assertEqual(res.data['event_date'], event_notification.event_date)
        self.assertEqual(res.data['location'], event_notification.location)
        self.assertEqual(res.data['entry_fee'], '10000.00')
        self.assertEqual(res.data['target_audience'], event_notification.target_audience)


class PrivateEventNotificationApiTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_event_notification(self):
        """Test creating an event notification"""
        payload = {
            'title': 'Uganda Tourism Board',
            'description': 'UTB is organizing a tourism expo',
            'event_date': '2022-01-01',
            'location': 'Kampala',
            'entry_fee': '10000.00',
            'target_audience': 'Tourists'
        }

        res = self.client.post(EVENT_NOTIFICATION_URL_API, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user to admin
        self.user.is_staff = True
        res = self.client.post(EVENT_NOTIFICATION_URL_API, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        event_notification = EventNotification.objects.get(id=res.data['id'])
        for key in payload.keys():
            if key == 'event_date':
                self.assertEqual(
                    datetime.strptime(payload[key], '%Y-%m-%d').date(),
                    getattr(event_notification, key)
                )
            elif key == 'entry_fee':
                self.assertEqual(Decimal(payload[key]), getattr(event_notification, key))
            else:
                self.assertEqual(payload[key], getattr(event_notification, key))

    def test_update_event_notification(self):
        """Test updating an event notification"""
        event_notification = create_event_notification(
            title='Uganda Tourism Board',
            description='UTB is organizing a tourism expo',
            event_date='2022-01-01',
            location='Kampala',
            entry_fee=Decimal('10000'),
            target_audience='Tourists'
        )

        payload = {
            'title': 'Uganda Tourism Board',
            'description': 'UTB is organizing a tourism expo',
            'event_date': '2022-01-01',
            'location': 'Kampala',
            'entry_fee': '10000.00',
            'target_audience': 'Tourists'
        }

        url = detail_url(event_notification.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user to admin
        self.user.is_staff = True
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        event_notification.refresh_from_db()
        for key in payload.keys():
            if key == 'event_date':
                self.assertEqual(
                    datetime.strptime(payload[key], '%Y-%m-%d').date(),
                    getattr(event_notification, key)
                )
            elif key == 'entry_fee':
                self.assertEqual(Decimal(payload[key]), getattr(event_notification, key))
            else:
                self.assertEqual(payload[key], getattr(event_notification, key))

    def test_delete_event_notification(self):
        """Test deleting an event notification"""
        event_notification = create_event_notification(
            title='Uganda Tourism Board',
            description='UTB is organizing a tourism expo',
            event_date='2022-01-01',
            location='Kampala',
            entry_fee=Decimal('10000'),
            target_audience='Tourists'
        )

        url = detail_url(event_notification.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change user to admin
        self.user.is_staff = True
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(EventNotification.objects.filter(id=event_notification.id).exists())
