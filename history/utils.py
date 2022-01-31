from post.models import Post
from .models import History
from datetime import datetime

def add_to_post_history(request, post: Post):
    if request.user.is_authenticated:
        user = request.user
        post = post
        id = str(user.id) + "-" + str(post.id)
        date = datetime.now()
        History.objects.update_or_create(id=id, user=user, post=post, defaults={'date': date})