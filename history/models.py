from django.db import models
from api.models import UserProfile
from post.models import Post

# Create your models here.


class History(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    user = models.ForeignKey(to=UserProfile, on_delete=models.CASCADE, related_name="post_history")
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE, related_name="watched")
    date = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'post'
        unique_together =(('user_id', 'post_id'),)