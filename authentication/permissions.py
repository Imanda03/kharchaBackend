from rest_framework import permissions
from rest_framework.generics import get_object_or_404
from .models import CustomUser


def is_user_customer_or_anonym(request):
    if request.user.is_authenticated:
        return request.user.role == 2
    else:
        return True


def is_user_customer(request):
    if request.user.is_authenticated:
        return request.user.role == 2
    else:
        return False


def is_user_admin(request):
    if request.user.is_authenticated:
        return request.user.role == 0
    return False


class IsCustomerOrAnonymPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return is_user_customer_or_anonym(request)


class OwnProfilePermissionUrl(permissions.BasePermission):

    def has_permission(self, request, view):
        user = CustomUser.objects.get(pk=view.kwargs['pk'])

        if request.user == user:
            return True
        else:
            return False


class OnlyAdminPostPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.method == 'POST' and request.user.role != 0:
                return False
            else:
                return True
        return False

class IsAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == 0:
            return True
        return False

class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAdminOrShopUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and (request.user.role == 0 or request.user.role == 1):
            return True
        return False

class IsCustomerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if(request.user.is_authenticated and request.user.role == 2):
            return True
        return False

class IsDontationOwnerOrReadOnlyPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS or is_user_admin(request):
            return True
        return obj.user == request.user
