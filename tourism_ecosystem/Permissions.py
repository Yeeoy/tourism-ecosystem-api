from rest_framework import permissions


# 自定义权限 - 只允许用户查看和修改自己的对象
class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # 管理员有所有权限
        if request.user.is_staff:
            return True
        # 普通用户只能查看和修改自己的对象
        return obj.user == request.user
