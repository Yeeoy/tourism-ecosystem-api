from decimal import Decimal

from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=255)
    venue = models.CharField(max_length=255)
    description = models.TextField()
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2)
    max_participants = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class VenueBooking(models.Model):
    event_id = models.ForeignKey('Event', on_delete=models.CASCADE)
    promotion_id = models.ForeignKey('EventPromotion', null=True, blank=True, on_delete=models.SET_NULL)
    user_id = models.ForeignKey('customUser.User', on_delete=models.CASCADE)
    booking_date = models.DateTimeField()
    booking_status = models.BooleanField(default=False)
    number_of_tickets = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Booking for {self.event_id.name}"

    def calculate_total_amount(self):
        # Ensure event and entry_fee exist
        if not self.event_id or not self.event_id.entry_fee:
            raise ValueError("Event and its entry fee are required to calculate the total amount.")

        # Use Decimal for monetary calculations
        ticket_price = Decimal(self.event_id.entry_fee)
        base_amount = ticket_price * self.number_of_tickets
        self.discount_amount = 0

        # Apply discount if there is a promotion
        if self.promotion_id:
            discount_amount = base_amount * (1 - Decimal(self.promotion_id.discount))
            self.discount_amount = discount_amount
            return base_amount - discount_amount

        # Return the original amount if there is no promotion
        return base_amount

    def save(self, *args, **kwargs):
        # Always calculate total_amount instead of relying on whether it is None
        self.total_amount = self.calculate_total_amount()
        super(VenueBooking, self).save(*args, **kwargs)


class EventPromotion(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    promotion_start_date = models.DateField()
    promotion_end_date = models.DateField()
    discount = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Promotion for {self.event.name}"