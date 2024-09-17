from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.event_organizers.models import VenueBooking, Event

VENUE_BOOKING_URL = reverse('event_organizers:venue-booking-list')


def create_venue_booking(**params):
    return VenueBooking.objects.create(**params)


def create_event(**params):
    return Event.objects.create(**params)


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def detail_url(venue_booking_id):
    return reverse('event_organizers:venue-booking-detail',
                   args=[venue_booking_id])


class PublicVenueBookingAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
