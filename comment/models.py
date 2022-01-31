from post.models import Post
from api.models import UserProfile
from django.db import models

# Create your models here.

class Comment(models.Model):
    user = models.ForeignKey(to=UserProfile, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE, related_name="comments")
    content = models.CharField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'post'

