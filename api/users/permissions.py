from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Allows access only to users with role 'admin'.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'admin')

class IsEmployee(permissions.BasePermission):
    """
    Allows access only to users with role 'employee'.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'employee')


class IsResident(permissions.BasePermission):
    """
    Allows access only to users with role 'resident'.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'resident')