from django.db import models
from django.contrib.auth.models import AbstractUser
import os
from uuid import uuid4

def image_name(instance, filename):
    ext = filename.split('.')[-1]
    return f'profile_image/{uuid4()}.{ext}'


# Create your models here.
class User(AbstractUser):
    private = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    image = models.ImageField(upload_to=image_name, null=True)

    def save(self, *args, **kwargs):
        if self.pk:
            old_image = User.objects.get(pk=self.pk).image
            if self.image != old_image and os.path.isfile(old_image.path):
                os.remove(old_image.path)
        super().save(*args, **kwargs)
    
