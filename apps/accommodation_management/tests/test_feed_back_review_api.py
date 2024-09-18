from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.accommodation_management.models import FeedbackReview, Accommodation

FEED_BACK_REVIEW_API_URL = reverse('accommodation_management:feedback-review-list')


def create_feed_back_review(**params):
    return FeedbackReview.objects.create(**params)


def create_user(email='user@example.com', password='password123'):
    return get_user_model().objects.create_user(email=email, password=password)


def detail_url(feed_back_review_id):
    return reverse('accommodation_management:feedback-review-detail', args=[feed_back_review_id])


class PublicFeedBackReviewAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

        self.accommodation = Accommodation.objects.create(
            name='Test Accommodation',
            location='Test Location',
            star_rating=4,
            total_rooms=100,
            amenities='Test amenities',
            type='Test type',
            check_in_time='09:00:00',
            check_out_time='17:00:00',
            contact_info='Test contact info'
        )

    def test_retrieve_feed_back_reviews(self):
        create_feed_back_review(
            accommodation_id=self.accommodation,
            user=self.user,
            rating=5,
            review='Test review',
            date='2021-09-01'
        )

        create_feed_back_review(
            accommodation_id=self.accommodation,
            user=self.user,
            rating=4,
            review='Test review 2',
            date='2021-09-02'
        )

        res = self.client.get(FEED_BACK_REVIEW_API_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_feed_back_review_detail(self):
        feed_back_review = create_feed_back_review(
            accommodation_id=self.accommodation,
            user=self.user,
            rating=5,
            review='Test review',
            date='2021-09-01'
        )

        res = self.client.get(detail_url(feed_back_review.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['rating'], 5)
        self.assertEqual(res.data['review'], 'Test review')
        self.assertEqual(res.data['date'], '2021-09-01')


class PrivateFeedBackReviewAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

        self.accommodation = Accommodation.objects.create(
            name='Test Accommodation',
            location='Test Location',
            star_rating=4,
            total_rooms=100,
            amenities='Test amenities',
            type='Test type',
            check_in_time='09:00:00',
            check_out_time='17:00:00',
            contact_info='Test contact info'
        )

    def test_create_feed_back_review(self):
        payload = {
            'accommodation_id': self.accommodation.id,
            'user': self.user.id,
            'rating': 5,
            'review': 'Test review',
            'date': '2021-09-01'
        }

        res = self.client.post(FEED_BACK_REVIEW_API_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['rating'], 5)
        self.assertEqual(res.data['review'], 'Test review')
        self.assertEqual(res.data['date'], payload['date'])

    def test_update_feed_back_review(self):

        user2 = create_user(
            email='user2@example.com',
            password='password123'
        )

        feed_back_review = create_feed_back_review(
            accommodation_id=self.accommodation,
            user=user2,
            rating=5,
            review='Test review',
            date='2021-09-01'
        )

        feed_back_review2 = create_feed_back_review(
            accommodation_id=self.accommodation,
            user=self.user,
            rating=5,
            review='Test review2',
            date='2021-09-02'
        )


        payload = {
            'rating': 4,
            'review': 'Test review updated',
            'date': '2021-09-03'
        }

        res = self.client.patch(detail_url(feed_back_review.id), payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        res = self.client.patch(detail_url(feed_back_review2.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        feed_back_review2.refresh_from_db()
        self.assertEqual(feed_back_review2.rating, 4)
        self.assertEqual(feed_back_review2.review, 'Test review updated')
        self.assertEqual(res.data['date'], payload['date'])

    def test_delete_feed_back_review(self):
        feed_back_review = create_feed_back_review(
            accommodation_id=self.accommodation,
            user=self.user,
            rating=5,
            review='Test review',
            date='2021-09-01'
        )

        res = self.client.delete(detail_url(feed_back_review.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(FeedbackReview.objects.filter(id=feed_back_review.id).exists())
