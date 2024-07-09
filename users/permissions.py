from django.contrib.auth.models import User
from follow.permissions import is_user_following

def is_user_accessble(request, user:User) ->bool:
    
    if user.id != request.user.id and user.is_private:
        if not request.user.is_authenticated or not is_user_following(request.user, user):
            return False
    return True