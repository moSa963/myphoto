from django.contrib.auth.models import User
from .models import Follow

def is_user_following(user: User, following: User) -> bool:
    follow = Follow.objects.filter(user_id=user.id, following_id=following.id).first()

    if follow and follow.is_verified:
        return True
    return False