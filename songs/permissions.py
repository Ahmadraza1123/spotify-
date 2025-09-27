from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


class IsSinger(BasePermission):

    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        if request.user.is_authenticated and getattr(request.user, "role", None) == "singer":
            return True

        raise PermissionDenied("Only singers can create or modify content.")


class IsNormalUser(BasePermission):

    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        if request.user.is_authenticated and getattr(request.user, "role", None) == "nuser":
            return True

        raise PermissionDenied("Only normal users can perform this action.")
