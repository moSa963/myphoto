from django.db import models
from django.contrib.auth.models import AbstractUser
import os;
import glob;
from myphoto import settings

# Create your models here.

def image_name(instance, filename):
    rest, suf = filename.rsplit('.', 1)
    username = instance.username or instance.user.username
    new_name = 'media/img/user/' + username + "." + suf

    #if there is a file with the same name delete it.
    for filepath in glob.glob(str(settings.BASE_DIR) + '/media/img/user/' + str(username) + '*'):
        name, end = os.path.basename(filepath).rsplit('.', 1)
        if name == username:
            os.remove(filepath)

    return new_name


class UserProfile(AbstractUser):
    is_private = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    image = models.ImageField(upload_to=image_name, null=True)