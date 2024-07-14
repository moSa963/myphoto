from typing import Any
from django.db import models
from users.models import User
from uuid import uuid4
from posts.manager import PostImageManager, PostManager
from django.core.files.storage import default_storage

# Create your models here.

class Post(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=50, default='')
    description = models.TextField(blank=True, default='')
    private = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)
    
    objects = PostManager()
    
    def __str__(self):
        return self.title
    
    def images_folder(self) -> str:
        return f'posts/{self.id}'
    
    def delete(self, *args, **kwargs):
        images = self.images.all()
        
        for image in images:
            image.delete()
        
        super(Post, self).delete(*args, **kwargs)
        

def image_name(instance, filename):
    ext = filename.split('.')[-1]
    return f'{instance.post.images_folder()}/{uuid4()}.{ext}'

class PostImage(models.Model):
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=image_name)

    objects = PostImageManager()
    
    def __str__(self):
        return self.image.url.split("/")[-1]
    
    def delete(self, *args, **kwargs):
        super(PostImage, self).delete(*args, **kwargs)
        
        if default_storage.exists(self.image.path):
            default_storage.delete(self.image.path)