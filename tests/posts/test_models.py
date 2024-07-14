from django.test import TestCase
from tests.helpers.post_helpers import createPost, getMediaRoot, addImageToPost
from django.test import override_settings
import shutil
from django.contrib.auth import get_user_model

@override_settings(MEDIA_ROOT=getMediaRoot())
class TestPostModel(TestCase):
    
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(username='admin', password='password')
        self.post = createPost(self.user, "title")
    
    def test_str(self):
        self.assertEqual(str(self.post), self.post.title)
    
    def test_images_folder(self):
        self.assertEqual(self.post.images_folder(), f"posts/{self.post.id}")

@override_settings(MEDIA_ROOT=getMediaRoot())
class TestPostModel(TestCase):
    
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(username='admin', password='password')
        post = createPost(self.user, "title")
        self.post_image = addImageToPost(post)
    
    def test_str(self):
        self.assertEqual(str(self.post_image), self.post_image.image.url.split("/")[-1])
    
def tearDownModule():
    shutil.rmtree(getMediaRoot(), ignore_errors=True)

