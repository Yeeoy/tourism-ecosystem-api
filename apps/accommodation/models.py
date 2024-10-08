from datetime import datetime

from django.db import models


class Accommodation(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    star_rating = models.PositiveIntegerField()
    total_rooms = models.PositiveIntegerField()
    amenities = models.TextField()
    type = models.CharField(max_length=255)
    check_in_time = models.TimeField()
    check_out_time = models.TimeField()
    contact_info = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class RoomType(models.Model):
    accommodation_id = models.ForeignKey('Accommodation', on_delete=models.CASCADE)
    room_type = models.CharField(max_length=255)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    max_occupancy = models.PositiveIntegerField()
    availability = models.BooleanField(default=True)

    def __str__(self):
        return self.room_type


class RoomBooking(models.Model):
    room_type_id = models.ForeignKey('RoomType', on_delete=models.CASCADE)
    accommodation_id = models.ForeignKey('Accommodation', on_delete=models.CASCADE)
    user_id = models.ForeignKey('customUser.User', on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    booking_status = models.BooleanField(default=False)
    payment_status = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Ensure check_in_date and check_out_date are date types
        if isinstance(self.check_in_date, str):
            self.check_in_date = datetime.strptime(self.check_in_date, '%Y-%m-%d').date()
        if isinstance(self.check_out_date, str):
            self.check_out_date = datetime.strptime(self.check_out_date, '%Y-%m-%d').date()

        # Calculate the total price
        self.total_price = self.room_type_id.price_per_night * (self.check_out_date - self.check_in_date).days
        super(RoomBooking, self).save(*args, **kwargs)


class GuestService(models.Model):
    accommodation_id = models.ForeignKey('Accommodation', on_delete=models.CASCADE)
    service_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability_hours = models.CharField(max_length=255)

    def __str__(self):
        return self.service_name


class FeedbackReview(models.Model):
    accommodation_id = models.ForeignKey('Accommodation', on_delete=models.CASCADE)
    user = models.ForeignKey('customUser.User', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    review = models.TextField()
    date = models.DateField()
