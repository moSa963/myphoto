from post.models import Post
from follow.permissions import is_user_following

def post_accessble(request, post: Post) -> bool:
    if request.user.is_authenticated and request.user.id == post.user_id:
        return True
    elif not post.is_private:
        if not post.user.is_private:
            return True
        else:
            if request.user.is_authenticated and is_user_following(request.user, post.user):
                return True
    return False
