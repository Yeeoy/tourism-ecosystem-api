from django.db import models


# Create your models here.
class Destination(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    opening_hours = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Tour(models.Model):
    destination = models.ForeignKey('Destination', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    tour_type = models.CharField(max_length=255)
    duration = models.CharField(max_length=255)
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    max_capacity = models.PositiveIntegerField()
    tour_date = models.DateField()
    guide_name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class EventNotification(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    event_date = models.DateField()
    location = models.CharField(max_length=255)
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2)
    target_audience = models.CharField(max_length=255)

    def __str__(self):
        return self.title
