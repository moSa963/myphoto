from django.db import models
from api.models import UserProfile
from post.models import Post
from comment.models import Comment

class Like(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    user = models.ForeignKey(to=UserProfile, on_delete=models.CASCADE, related_name="liking")
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE, related_name="likes")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'post'
        unique_together =(('user_id', 'post_id'),)


class CommentLike(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    user = models.ForeignKey(to=UserProfile, on_delete=models.CASCADE)
    comment = models.ForeignKey(to=Comment, on_delete=models.CASCADE, related_name="likes")
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'comment'
        unique_together =(('user_id', 'comment_id'),)
