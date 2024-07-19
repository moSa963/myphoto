from django.core.exceptions import PermissionDenied
from relations.models import Follow



def is_user_accessible(request, user):
    if user.id != request.user.id and user.private:
        if not Follow.objects.filter(user_id=request.user.id, followed_user__id=user.id, verified=True).exists():
            raise PermissionDenied("You cannot access this user information.")

    return True