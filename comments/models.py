from django.db import models
from users.models import User
from posts.models import Post
# Create your models here.


class PostComment(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now=True)

class CommentLike(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='comments_likes')
    comment = models.ForeignKey(to=PostComment, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = (('user_id', 'comment_id'),)