from django.db import models
from api.models import UserProfile

# Create your models here.
class Follow(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    user = models.ForeignKey(to=UserProfile, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(to=UserProfile, on_delete=models.CASCADE, related_name='followers')
    is_verified = models.BooleanField(default=False)
    following_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'follow'
        unique_together =(('user_id', 'following_id'),)