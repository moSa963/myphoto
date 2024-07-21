from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.test import override_settings
import shutil
from tests.helpers.comment_helper import create_comment
from tests.helpers.post_helpers import createPost, getMediaRoot
from tests.helpers.user_helpers import create_user 
from comments.models import CommentLike

TEST_DIR = getMediaRoot()

@override_settings(MEDIA_ROOT=TEST_DIR)
class TestCommentView(APITestCase):
    def setUp(self):
        self.user = create_user(username='admin', password='password')
        self.client = APIClient()
        self.client.login(username='admin', password='password')

    def test_user_can_comment_on_post(self):
        post = createPost(create_user(username="username"), "title")
        
        data={ "content": "this is a test comment" }
        
        response = self.client.post(
            reverse("comments:create", kwargs={"post_id": post.id}), 
            data=data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        js = response.json()
        self.assertEqual(js["user"]["username"], self.user.username)
        self.assertEqual(js["content"], data["content"])
    
    def test_user_cannot_comment_on_a_private_post(self):
        post = createPost(create_user(username="username"), "title", private=True)
        
        response = self.client.post(
            reverse("comments:create", kwargs={"post_id": post.id}), 
            data={ "content": "this is a test comment" }
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_cannot_comment_on_a_post_whose_owner_is_private(self):
        post = createPost(create_user(username="username", private=True), "title")
        
        response = self.client.post(
            reverse("comments:create", kwargs={"post_id": post.id}), 
            data={ "content": "this is a test comment" }
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        
    def test_user_can_delete_a_comment_on_post(self):
        post = createPost(create_user(username="username"), "title")
        comment = create_comment(self.user, post)

        self.assertEqual(post.comments.count(), 1)

        response = self.client.delete(
            reverse("comments:delete", kwargs={"post_id": post.id, "id": comment.id}), 
        )
            
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(post.comments.count(), 0)


@override_settings(MEDIA_ROOT=TEST_DIR)
class TestCommentsListView(APITestCase):
    def setUp(self):
        self.user = create_user(username='admin', password='password')
        self.client = APIClient()
        self.client.login(username='admin', password='password')

    def test_user_can_get_a_comments_list(self):
        post = createPost(create_user(username="username"), "title")
        create_comment(self.user, post)
        create_comment(create_user(username="username2"), post)
        create_comment(create_user(username="username3"), post)
    
        response = self.client.get(reverse('comments:list', kwargs={"post_id": post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        js = response.json()
        self.assertEqual(len(js["results"]), 3)



@override_settings(MEDIA_ROOT=getMediaRoot())
class TestCommentLikeView(APITestCase):
    
    def setUp(self) -> None:
        self.user = create_user(username='admin', password='password')
        self.client = APIClient()
        self.client.login(username='admin', password='password')
        
    
    def test_user_can_like_a_comment(self):
        post = createPost(create_user(username="username"), "title")
        comment = create_comment(create_user(username="username2"), post)
        
        self.assertEqual(comment.likes.count(), 0)
        
        response = self.client.post(reverse("comments:like", kwargs={
            "post_id": post.id,
            "id": comment.id,
        }))
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.assertEqual(comment.likes.count(), 1)
    
    def test_user_cannot_like_a_comment_on_private_post(self):
        post = createPost(create_user(username="username"), "title", private=True)
        comment = create_comment(create_user(username="username2"), post)
        
        response = self.client.post(reverse("comments:like", kwargs={
            "post_id": post.id,
            "id": comment.id,
        }))
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_cannot_like_a_comment_created_by_a_private_user(self):
        post = createPost(create_user(username="username", private=True), "title")
        comment = create_comment(create_user(username="username2"), post)
        
        response = self.client.post(reverse("comments:like", kwargs={
            "post_id": post.id,
            "id": comment.id,
        }))
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_user_can_unlike_a_post(self):
        post = createPost(create_user(username="username"), "title")
        comment = create_comment(create_user(username="username2"), post)
        
        CommentLike.objects.create(user_id=self.user.id, comment_id=comment.id)
        
        self.assertEqual(comment.likes.count(), 1)
        
        response = self.client.delete(reverse("comments:like", kwargs={
            "post_id": post.id,
            "id": comment.id,
        }))
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


def tearDownModule():
    shutil.rmtree(TEST_DIR, ignore_errors=True)