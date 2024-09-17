from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.event_organizers.models import EventPromotion, Event
from apps.event_organizers.serializers import EventPromotionSerializer

EVENT_PROMOTION_URL = reverse('event_organizers:event-promotion-list')


def create_event(**params):
    return Event.objects.create(**params)


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def create_event_promotion(**params):
    return EventPromotion.objects.create(**params)


def detail_url(event_promotion_id):
    return reverse(
        'event_organizers:event-promotion-detail',
        args=[event_promotion_id]
    )


class PubicEventPromotionAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_event_promotions(self):
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

        create_event_promotion(
            event=event,
            promotion_start_date='2021-03-01',
            promotion_end_date='2021-03-31',
            discount=0.9
        )

        res = self.client.get(EVENT_PROMOTION_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_retrieve_event_promotion_detail(self):
        event_promotion = create_event_promotion(
            event=create_event(
                name='Test Event',
                venue='Test Location',
                description='Test description',
                event_date='2021-03-01',
                start_time='09:00:00',
                end_time='17:00:00',
                entry_fee=30.00,
                max_participants=300
            ),
            promotion_start_date='2021-03-01',
            promotion_end_date='2021-03-31',
            discount=0.9
        )

        res = self.client.get(detail_url(event_promotion.id))

        serializer = EventPromotionSerializer(event_promotion)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class PrivateEventPromotionAPITests(TestCase):

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_event_promotion(self):
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

        payload = {
            'event': event.id,
            'promotion_start_date': '2021-03-01',
            'promotion_end_date': '2021-03-31',
            'discount': 0.9
        }

        res = self.client.post(EVENT_PROMOTION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        event_promotion = EventPromotion.objects.get(id=res.data['id'])
        self.assertEqual(event_promotion.discount, payload['discount'])

    def test_update_event_promotion(self):
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

        event_promotion = create_event_promotion(
            event=event,
            promotion_start_date='2021-03-01',
            promotion_end_date='2021-03-31',
            discount=0.9
        )

        payload = {
            'discount': 0.8
        }

        url = detail_url(event_promotion.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change to admin user
        self.user.is_staff = True
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        event_promotion.refresh_from_db()
        self.assertEqual(
            event_promotion.discount,
            Decimal(str(payload['discount']))
        )

    def test_delete_event_promotion(self):
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

        event_promotion = create_event_promotion(
            event=event,
            promotion_start_date='2021-03-01',
            promotion_end_date='2021-03-31',
            discount=0.9
        )

        url = detail_url(event_promotion.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # change to admin user
        self.user.is_staff = True
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(EventPromotion.objects
                         .filter(id=event_promotion.id).exists())
