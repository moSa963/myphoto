from django.db import models
from users.models import User

# Create your models here.
class Follow(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='following')
    followed_user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='followers')
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together =(('user_id', 'followed_user_id'),)
    
    def set_verified(self):
        self.verified = True
        self.save()