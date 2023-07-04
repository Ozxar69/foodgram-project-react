from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminAuthorOrReadOnly(BasePermission):
    """Права доступа для автора либо алминистратора."""
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user.is_superuser
                or request.user.is_staff
                or obj.author == request.user)
