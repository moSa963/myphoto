from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient, APITransactionTestCase
from rest_framework import status
from django.test import override_settings
import shutil
from django.core.files.storage import default_storage
from tests.helpers.post_helpers import createPost, addImageToPost, createImage, getMediaRoot, like_post
from tests.helpers.user_helpers import create_user 
from tests.helpers.relation_helpers import create_follow 
from posts.models import PostLike

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
        self.assertEqual(len(js["results"]), 2)
            
        
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
        
        
@override_settings(MEDIA_ROOT=getMediaRoot())
class TestPostLikeView(APITransactionTestCase):
    
    def setUp(self) -> None:
        self.user = create_user(username='admin', password='password')
        self.client = APIClient()
        self.client.login(username='admin', password='password')
        
    
    def test_user_can_like_a_post(self):
        post = createPost(create_user(username="username"), "title")
        
        self.assertEqual(post.likes.count(), 0)
        
        response = self.client.post(reverse("posts:like", kwargs={
            "id": post.id,
        }))
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.assertEqual(post.likes.count(), 1)
    
    def test_user_cannot_like_a_private_post(self):
        post = createPost(create_user(username="username"), "title", private=True)
        
        self.assertEqual(post.likes.count(), 0)
        
        response = self.client.post(reverse("posts:like", kwargs={
            "id": post.id,
        }))
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.assertEqual(post.likes.count(), 0)
    
    def test_user_cannot_like_a_post_created_by_a_private_user(self):
        post = createPost(create_user(username="username", private=True), "title")
        
        self.assertEqual(post.likes.count(), 0)
        
        response = self.client.post(reverse("posts:like", kwargs={
            "id": post.id,
        }))
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.assertEqual(post.likes.count(), 0)
        
    def test_user_can_unlike_a_post(self):
        post = createPost(create_user(username="username"), "title")
        PostLike.objects.create(user_id=self.user.id, post_id=post.id)
        
        self.assertEqual(post.likes.count(), 1)
        
        response = self.client.delete(reverse("posts:like", kwargs={
            "id": post.id,
        }))
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.assertEqual(post.likes.count(), 0)

@override_settings(MEDIA_ROOT=getMediaRoot())
class TestPostLikeListView(APITransactionTestCase):
    
    def setUp(self) -> None:
        self.user = create_user(username='admin', password='password')
        self.client = APIClient()
        self.client.login(username='admin', password='password')
        
    
    def test_user_can_get_a_list_of_users_who_liked_a_post(self):
        post = createPost(create_user(username="username"), "title")
        
        like_post(self.user, post)
        like_post(create_user(username="user1"), post)
        like_post(create_user(username="user2", private=True), post)
        user3 = create_user(username="user3", private=True)
        create_follow(self.user, user3)
        like_post(user3, post)
        
        
        self.assertEqual(post.likes.count(), 4)
        
        response = self.client.get(reverse("posts:like_list", kwargs={
            "id": post.id,
        }))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        js = response.json()
        self.assertEqual(len(js["results"]), 3)

@override_settings(MEDIA_ROOT=getMediaRoot())
class TestUsersPostsListView(APITransactionTestCase):
    
    def setUp(self) -> None:
        self.user = create_user(username='admin', password='password')
        self.client = APIClient()
        self.client.login(username='admin', password='password')
    
    def test_user_can_get_his_posts_list(self):
        createPost(self.user, "title")
        createPost(self.user, "title2")
        createPost(create_user(username="user", private=True), "title4")
        
        response = self.client.get(reverse('posts:users_list', kwargs={"username": self.user.username}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        js = response.json()
        self.assertEqual(len(js["results"]), 2)
    
    def test_user_can_get_a_user_posts_list(self):
        user = create_user(username="username1")
        createPost(user, "title")
        createPost(user, "title2")
        createPost(user, "title3", private=True)
        
        response = self.client.get(reverse('posts:users_list', kwargs={"username": user.username}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        js = response.json()
        self.assertEqual(len(js["results"]), 2)
        
    def test_user_cannot_get_a_private_user_posts_list(self):
        user = create_user(username="username1", private=True)
        createPost(user, "title")
        
        response = self.client.get(reverse('posts:users_list', kwargs={"username": user.username}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

@override_settings(MEDIA_ROOT=getMediaRoot())
class TestUsersLikedPostsListView(APITransactionTestCase):
    
    def setUp(self) -> None:
        self.user = create_user(username='admin', password='password')
        self.client = APIClient()
        self.client.login(username='admin', password='password')
    
    def test_user_can_get_his_liked_posts(self):
        like_post(self.user, createPost(create_user(username="username1"), "title"))
        like_post(self.user, createPost(self.user, "title2"))
        like_post(self.user, createPost(create_user(username="username2"), "title", private=True))
        like_post(self.user, createPost(create_user(username="user", private=True), "title4"))
        
        response = self.client.get(reverse('posts:users_liked_list', kwargs={"username": self.user.username}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        js = response.json()
        self.assertEqual(len(js["results"]), 2)
    
    def test_user_can_get_a_user_liked_posts(self):
        user = create_user(username="username")
        like_post(user, createPost(create_user(username="username1"), "title"))
        like_post(user, createPost(self.user, "title2"))
        like_post(user, createPost(create_user(username="username2"), "title", private=True))
        like_post(user, createPost(create_user(username="user", private=True), "title4"))
        
        response = self.client.get(reverse('posts:users_liked_list', kwargs={"username": user.username}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        js = response.json()
        self.assertEqual(len(js["results"]), 2)
    
    def test_user_cannot_get_a_private_user_liked_posts(self):
        user = create_user(username="username", private=True)
        like_post(user, createPost(create_user(username="username1"), "title"))
        
        response = self.client.get(reverse('posts:users_liked_list', kwargs={"username": user.username}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
def tearDownModule():
    shutil.rmtree(TEST_DIR, ignore_errors=True)