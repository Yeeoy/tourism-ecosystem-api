from rest_framework import permissions
from rest_framework.permissions import BasePermission


# Custom permission - only allows users to view and modify their own objects
class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Admin has all permissions
        if request.user.is_staff:
            return True
        # Regular users can only view and modify their own objects
        return obj.user == request.user


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        # Write permissions are only allowed to the admin users.
        return request.user and request.user.is_staff
