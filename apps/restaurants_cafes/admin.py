from django.contrib import admin
from .models import Restaurant, TableReservation, Menu, OnlineOrder, OrderItem


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'cuisine_type', 'opening_hours', 'contact_info')
    search_fields = ('name', 'location', 'cuisine_type')
    list_filter = ('cuisine_type',)


@admin.register(TableReservation)
class TableReservationAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'user', 'reservation_date', 'reservation_time', 'number_of_guests', 'reservation_status')
    search_fields = ('restaurant__name', 'user__username')
    list_filter = ('reservation_date', 'reservation_status')


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'item_name', 'price')
    search_fields = ('item_name', 'restaurant__name')
    list_filter = ('restaurant',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('subtotal',)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Filter the menu items to only show the ones that belong to the same restaurant as the order.
        """
        if db_field.name == 'menu_item' and request._obj_ is not None:
            # Filter the menu items based on the restaurant of the current order
            kwargs['queryset'] = Menu.objects.filter(restaurant=request._obj_.restaurant)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(OnlineOrder)
class OnlineOrderAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'user', 'order_date', 'order_time', 'total_amount', 'order_status')
    search_fields = ('restaurant__name', 'user__username', 'order_status')
    list_filter = ('order_date', 'order_status')
    inlines = [OrderItemInline]

    def get_form(self, request, obj=None, **kwargs):
        """
        Store the current object (OnlineOrder) on the request for use in formfield_for_foreignkey.
        """
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)

    # Automatically calculate the total amount based on order items in the admin
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.calculate_total_amount()
