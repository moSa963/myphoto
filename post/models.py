from django.db import models
from api.models import UserProfile
from django.core.files.storage import default_storage
# Create your models here.

class Post(models.Model):
    user = models.ForeignKey(to=UserProfile, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=50, default='')
    description = models.CharField(max_length=1000, default='')
    is_private = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'post'

class Image(models.Model):
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='media/img/post')

    class Meta:
        app_label = 'post'

    def delete_file(self):
        path = self.image
        if default_storage.exists(str(path)):
            default_storage.delete(str(path))