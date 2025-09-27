from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import PermissionDenied

class IsSinger(BasePermission):
    """
    Only users with role='singer' can create/update/delete artists.
    Normal users can only read.
    """

    def has_permission(self, request, view):
        # Read-only requests allowed
        if request.method in SAFE_METHODS:
            return True


        if request.user.is_authenticated and getattr(request.user, "role", None) == "singer":
            return True

        raise PermissionDenied("Only singers can create or modify artists.")
