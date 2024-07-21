from comments.models import PostComment


def create_comment(user, post):
    
    return PostComment.objects.create(
        user_id=user.id,
        post_id=post.id,
        content="this is a comment",
    )