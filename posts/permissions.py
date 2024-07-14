from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        is_authenticated = permissions.IsAuthenticated().has_permission(request, view)
        
        return is_authenticated and request.method in permissions.SAFE_METHODS
    
    def has_object_permission(self, request, view, obj):
        is_authenticated = permissions.IsAuthenticated().has_permission(request, view)
        
        return is_authenticated and (request.method in permissions.SAFE_METHODS or obj.user == request.user)
    
class IsOwner(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user