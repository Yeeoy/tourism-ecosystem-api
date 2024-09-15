from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.user import models


class UserAdmin(BaseUserAdmin):
    # 定义后台管理页面中用户列表的排序方式，这里是按照用户ID升序排序。
    ordering = ["id"]
    # 在用户列表页面显示用户的email和name字段，方便管理员快速查看重要信息。
    list_display = ["email", "name"]
    # 定义了用户编辑页面的字段布局，将不同类别的字段分组展示。
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
    # 指定last_login字段为只读
    # 管理员在后台无法修改这个字段
    # 它会自动更新为用户的上次登录时间
    readonly_fields = ["last_login"]
    add_fieldsets = (
        (
            None,
            {
                # 是一个CSS类，用来让表单显示得更加宽敞
                "classes": ("wide",),
                # 定义了用户编辑页面的字段布局，将不同类别的字段分组展示
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


# 模型注册到Django Admin中，使管理员可以通过后台界面管理这些模型的数据。
admin.site.register(models.User, UserAdmin)
