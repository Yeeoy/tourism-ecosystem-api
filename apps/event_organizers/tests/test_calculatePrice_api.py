from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.event_organizers.models import Event, EventPromotion

CALCULATE_URL = reverse('event_organizers:venue-booking-calculate-price')


class CalculatePriceAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = self.create_user(
            email='test@example.com', password='testpassword'
        )
        self.client.force_authenticate(self.user)
        self.event = self.create_event(
            name='Concert',
            venue='Stadium',
            description='Live Concert',
            event_date=timezone.now().date(),
            start_time='18:00',
            end_time='22:00',
            entry_fee=50.00,  # fares
            max_participants=500
        )

    def create_user(self, **params):
        return get_user_model().objects.create_user(**params)

    def create_event(self, **params):
        return Event.objects.create(**params)

    def test_calculate_price_without_promotion(self):
        """Test total amount calculation without promotion"""
        payload = {
            'event': self.event.id,
            'number_of_tickets': 2
        }

        res = self.client.post(CALCULATE_URL, payload)

        expected_total = self.event.entry_fee * 2  # 50 * 2 = 100

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(res.data['total_amount']), expected_total)

    def test_calculate_price_with_promotion(self):
        """Test total amount calculation with promotion"""
        discount = Decimal('0.80')
        # Create promotion with 20% discount
        EventPromotion.objects.create(
            event=self.event,
            promotion_start_date=timezone.now().date(),
            promotion_end_date=timezone.now().date() + timedelta(days=10),
            discount=discount
        )

        payload = {
            'event': self.event.id,
            'number_of_tickets': 2
        }

        res = self.client.post(CALCULATE_URL, payload)

        # Ensure using Decimal for monetary calculations
        base_amount = Decimal(self.event.entry_fee) * Decimal(2)
        # Discounted price (100 * 0.80 = 80)
        expected_total = base_amount * Decimal(discount)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(res.data['total_amount']), expected_total)


def test_calculate_price_with_invalid_event(self):
    """Test response when event does not exist"""
    payload = {
        'event': 999,  # Non-existent event ID
        'number_of_tickets': 2
    }

    res = self.client.post(CALCULATE_URL, payload)

    self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
    self.assertIn('Event not found.', res.data['detail'])


def test_calculate_price_with_invalid_tickets(self):
    """Test handling of invalid ticket count (negative number)"""
    payload = {
        'event': self.event_id.id,
        'number_of_tickets': -5  # Invalid ticket count
    }

    res = self.client.post(CALCULATE_URL, payload)

    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertIn(
        'The number of tickets must be a positive integer.',
        res.data['number_of_tickets'][0]
    )
