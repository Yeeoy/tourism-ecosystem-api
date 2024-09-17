# Create your models here.
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
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    booking_date = models.DateTimeField()
    booking_status = models.BooleanField(default=False)
    number_of_tickets = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    promotion = models.ForeignKey('EventPromotion', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Booking for {self.event.name}"

    def calculate_total_amount(self):
        # 确保 event 和 entry_fee 存在
        if not self.event or not self.event.entry_fee:
            raise ValueError("Event and its entry fee are required to calculate the total amount.")

        # 使用 Decimal 进行金额计算
        ticket_price = Decimal(self.event.entry_fee)
        base_amount = ticket_price * self.number_of_tickets

        # 如果有促销，应用折扣
        if self.promotion:
            discount_amount = base_amount * (Decimal(self.promotion.discount) / Decimal(100))
            return base_amount - discount_amount

        # 没有促销时返回原始金额
        return base_amount

    def save(self, *args, **kwargs):
        # 总是计算 total_amount 而不是依赖于它是否为 None
        self.total_amount = self.calculate_total_amount()
        super(VenueBooking, self).save(*args, **kwargs)


class EventPromotion(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    promotion_start_date = models.DateField()
    promotion_end_date = models.DateField()
    discount = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Promotion for {self.event.name}"
