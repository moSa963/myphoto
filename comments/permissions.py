from django.core.exceptions import PermissionDenied

    
    
def is_owner(request, comment):
    
    if request.user.id == comment.user_id:
        return True
    
    raise PermissionDenied()