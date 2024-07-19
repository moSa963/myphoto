from rest_framework import permissions
from relations.permissions import is_user_accessible
from django.core.exceptions import PermissionDenied



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
    

def is_post_accessible(request, post):
    if post.user_id == request.user.id:
        return
    
    if not post.private and is_user_accessible(request, post.user):
        return
    
    raise PermissionDenied()