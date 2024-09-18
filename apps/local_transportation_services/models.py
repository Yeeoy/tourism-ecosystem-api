# Create your models here.
from datetime import datetime

from django.db import models


class TransportationProvider(models.Model):
    name = models.CharField(max_length=255)
    service_type = models.CharField(max_length=255)
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_km = models.DecimalField(max_digits=10, decimal_places=2)
    contact_info = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class RideBooking(models.Model):
    user = models.ForeignKey('customUser.User', on_delete=models.CASCADE)
    provider_id = models.ForeignKey('TransportationProvider', on_delete=models.CASCADE)
    pickup_location = models.CharField(max_length=255)
    drop_off_location = models.CharField(max_length=255)
    ride_date = models.DateField()
    pickup_time = models.TimeField()
    estimated_fare = models.DecimalField(max_digits=10, decimal_places=2)
    booking_status = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # 确保 ride_date 是日期类型
        if isinstance(self.ride_date, str):
            self.ride_date = datetime.strptime(self.ride_date, '%Y-%m-%d').date()
        super(RideBooking, self).save(*args, **kwargs)

    def __str__(self):
        return self.pickup_location


class RoutePlanning(models.Model):
    provider_id = models.ForeignKey('TransportationProvider', on_delete=models.CASCADE)
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    distance = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_time = models.CharField(max_length=255)

    def __str__(self):
        return self.start_location


class TrafficUpdate(models.Model):
    provider_id = models.ForeignKey('TransportationProvider', on_delete=models.CASCADE)
    update_time = models.DateTimeField()
    update_message = models.TextField()

    def save(self, *args, **kwargs):
        # 确保 update_time 是日期时间类型
        if isinstance(self.update_time, str):
            self.update_time = datetime.strptime(self.update_time, '%Y-%m-%d %H:%M:%S')
        super(TrafficUpdate, self).save(*args, **kwargs)

    def __str__(self):
        return self.update_message
