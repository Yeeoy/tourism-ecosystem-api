from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.customUser import models


class UserAdmin(BaseUserAdmin):
    # Define the ordering of the user list in the admin page, here it is sorted by user ID in ascending order.
    ordering = ["id"]
    # Display the email and name fields in the user list page, allowing administrators to quickly view important information.
    list_display = ["email", "name"]
    # Define the field layout of the user edit page, grouping different categories of fields.
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Permissions"),
            {"fields": ("is_active", "is_staff", "is_superuser")}
        ),
        (
            _("Important dates"), {"fields": ("last_login",)}
        ),
    )
    # Specify the last_login field as read-only
    # Administrators cannot modify this field in the admin
    # It will automatically update to the user's last login time
    readonly_fields = ["last_login"]
    add_fieldsets = (
        (
            None,
            {
                # A CSS class to make the form display more spacious
                "classes": ("wide",),
                # Define the field layout of the user edit page, grouping different categories of fields
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "name",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


# Register the model to the Django Admin, allowing administrators to manage the model data through the admin interface.
admin.site.register(models.User, UserAdmin)
