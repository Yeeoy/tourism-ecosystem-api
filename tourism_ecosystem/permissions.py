from rest_framework import permissions
from rest_framework.permissions import BasePermission


# 自定义权限 - 只允许用户查看和修改自己的对象
class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # 管理员有所有权限
        if request.user.is_staff:
            return True
        # 普通用户只能查看和修改自己的对象
        return obj.user == request.user


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        # Write permissions are only allowed to the admin users.
        return request.user and request.user.is_staff
