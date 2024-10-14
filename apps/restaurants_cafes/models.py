from django.db import models


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    cuisine_type = models.CharField(max_length=255)
    opening_hours = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255)
    img_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class TableReservation(models.Model):
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE)
    user = models.ForeignKey('customUser.User', on_delete=models.CASCADE)
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    number_of_guests = models.PositiveIntegerField()
    reservation_status = models.CharField(max_length=255)

    def __str__(self):
        return self.restaurant.name


class Menu(models.Model):
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.item_name


class OnlineOrder(models.Model):
    user = models.ForeignKey('customUser.User', on_delete=models.CASCADE)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE)
    order_date = models.DateField()
    order_time = models.TimeField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(max_length=255)

    def __str__(self):
        return self.restaurant.name

    # A method to calculate total amount from related OrderItems
    def calculate_total_amount(self):
        total = sum(item.subtotal() for item in self.order_items.all())
        self.total_amount = total
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey('OnlineOrder', related_name='order_items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey('Menu', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.item_name} for {self.order}"

    # Subtotal for each menu item
    def subtotal(self):
        return self.menu_item.price * self.quantity

    def save(self, *args, **kwargs):
        # Ensure the menu item belongs to the same restaurant as the order
        if self.menu_item.restaurant != self.order.restaurant:
            raise ValueError(f"The menu item '{self.menu_item}' does not belong to the restaurant of the order.")
        super().save(*args, **kwargs)
