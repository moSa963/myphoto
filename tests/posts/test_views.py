from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient, APITransactionTestCase
from rest_framework import status
from django.test import override_settings
import shutil
from django.core.files.storage import default_storage
from tests.helpers.post_helpers import createPost, addImageToPost, createImage, getMediaRoot
from tests.helpers.user_helpers import create_user 

TEST_DIR = getMediaRoot()

@override_settings(MEDIA_ROOT=TEST_DIR)
class TestPostView(APITransactionTestCase):
    def setUp(self):
        self.user = create_user(username='admin', password='password')
        self.client = APIClient()
        self.client.login(username='admin', password='password')
    
    def test_user_can_get_a_post(self):
        post = createPost(self.user, "this is a test")
        
        response = self.client.get(reverse('posts:show', kwargs={ "id": post.id }))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        js = response.json()

        self.assertEqual(js["title"], 'this is a test')
        self.assertEqual(len(js["images"]), 1)
    
    
    def test_user_can_create_a_new_post(self):
        image_io = createImage()
        
        data = {
            "title": "this is the test title",
            "images": SimpleUploadedFile("test_image.jpg", image_io.read(), content_type='image/jpeg'),
        }
        
        response = self.client.post(reverse('posts:create'), data=data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        js = response.json()    
        self.assertEqual(js["title"], 'this is the test title')
        self.assertEqual(len(js["images"]), 1)
    
    def test_user_can_delete_a_post(self):
        shutil.rmtree(TEST_DIR, ignore_errors=True)
        post = createPost(self.user, "this is a test")
        addImageToPost(post)
        addImageToPost(post)
        
        self.assertEqual(post.images.count(), 3)
        self.assertEqual(len(default_storage.listdir(post.images_folder())[1]), 3)
        
        
@override_settings(MEDIA_ROOT=TEST_DIR)
class TestPostListView(APITransactionTestCase):
    def setUp(self):
        self.user = create_user(username='admin', password='password')
        self.client = APIClient()
        self.client.login(username='admin', password='password')
    
    def test_user_can_get_a_list_of_related_posts(self):
        createPost(self.user, "title")
        createPost(self.user, "title2")
        
        createPost(create_user(username="user", password="pass", private=True), "title4")
        
        response = self.client.get(reverse('posts:list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        js = response.json()
        self.assertEqual(len(js), 2)
            
        
@override_settings(MEDIA_ROOT=getMediaRoot())
class TestPostImageView(APITransactionTestCase):
    
    def setUp(self) -> None:
        self.user = create_user(username='admin', password='password')
        self.client = APIClient()
        self.client.login(username='admin', password='password')
    
    def test_user_can_get_a_post_image(self):
        post = createPost(self.user, "title")
        image = post.images.first()
        
        self.assertNotEqual(image, None)
        
        response = self.client.get(reverse("posts:image", kwargs={
            "id": post.id,
            "name": str(image)
        }))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertTrue(
            response.get('Content-Disposition').endswith(f'filename="{str(image)}"')
        )
        
        

        
def tearDownModule():
    shutil.rmtree(TEST_DIR, ignore_errors=True)