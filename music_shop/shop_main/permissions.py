from typing import Any
from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnly(BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.method in SAFE_METHODS


class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsOwnerOrStaffOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj: Any) -> bool:
        if request.method in SAFE_METHODS:
            return True
        user = getattr(obj, "user", None)
        if user is not None and request.user.is_authenticated:
            if request.user == user:
                return True
        return bool(request.user and request.user.is_staff)

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)
