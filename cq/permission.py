from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it
    """

    def has_object_permission(self, request, view, obj):
        # 읽기 : 모두 허용 -> GET, HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True

        # 쓰기 : 작성자만
        return obj.owner == request.user


class CustomUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method == 'POST' or request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        if request.method == 'POST':
            return True
        return request.user.is_superuser or request.user == obj


class CustomProfilePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        if request.method == 'POST':
            return True
        return request.user.is_superuser or request.user == obj.user
