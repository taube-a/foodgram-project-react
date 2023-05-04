from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    message = 'Редактирование чужого контента невозможно.'

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)


class IsAdminOrReadOnly(permissions.BasePermission):
    message = 'Редактирование контента возможно только Администратором.'

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_staff)
