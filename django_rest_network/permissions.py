from rest_framework import permissions

SAFE_METHODS = ['POST', 'PUT']

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return obj.author == request.user
        return True