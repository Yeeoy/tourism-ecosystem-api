from django.db import models
from django.utils import timezone


class Attraction(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    opening_hours = models.CharField(max_length=50)
    closing_hours = models.CharField(max_length=50)
    is_open = models.BooleanField(default=True)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Museum(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    opening_hours = models.CharField(max_length=50)
    closing_hours = models.CharField(max_length=50)
    is_open = models.BooleanField(default=True)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)
    attractions = models.ManyToManyField(Attraction, related_name='museums')

    def __str__(self):
        return self.name


class TourGuide(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()
    available_from = models.TimeField()
    available_to = models.TimeField()
    languages = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    attraction = models.ForeignKey('Attraction',
                                   on_delete=models.CASCADE,
                                   null=True,
                                   blank=True)
    museum = models.ForeignKey('Museum',
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)  # 确保该字段不能为空
    purchase_date = models.DateTimeField()
    valid_until = models.DateTimeField()

    def __str__(self):
        return f"Ticket for {self.attraction.name or self.museum.name}"


class Booking(models.Model):
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    guide = models.ForeignKey(TourGuide, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(default=timezone.now)
    visit_date = models.DateTimeField()

    def __str__(self):
        return (f"Booking for "
                f"{self.ticket.attraction.name or self.ticket.museum.name} "
                f"on {self.visit_date}")


class EducationContent(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    related_attraction = models.ForeignKey(Attraction,
                                           on_delete=models.CASCADE)
    related_museum = models.ForeignKey(Museum,
                                       on_delete=models.CASCADE)
    content_url = models.URLField()

    def __str__(self):
        return self.title
