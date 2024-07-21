from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from relations.models import Follow
from tests.helpers.user_helpers import create_user
from tests.helpers.relation_helpers import create_follow


class TestFollowView(APITestCase):
    def setUp(self):
        self.user = create_user(username='admin', password='password')
        self.other_user = create_user(username='other', password='password')
        self.client = APIClient()
        self.client.login(username='admin', password='password')
    
    def test_user_can_follow_other_user(self):
        self.assertEqual(self.user.following.count(), 0)
        
        response = self.client.post(reverse("relations:follow", kwargs={"username": self.other_user.username}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        js = response.json()
        self.assertEqual(js["user"]["username"], self.user.username)
        self.assertEqual(js["followed_user"]["username"], self.other_user.username)
        self.assertEqual(js["verified"], True)
    
    def test_user_can_unfollow_other_user(self):
        Follow.objects.create(user=self.user, followed_user=self.other_user)
        
        self.assertEqual(self.user.following.count(), 1)
        
        response = self.client.delete(reverse("relations:follow", kwargs={"username": self.other_user.username}))
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.assertEqual(self.user.following.count(), 0)
    
class TestAcceptFollowView(APITestCase):
    def setUp(self):
        user = create_user(username='admin', password='password')
        other_user = create_user(username='other', password='password', private=True)
        self.client = APIClient()
        self.client.login(username='admin', password='password')
        self.follow = Follow.objects.create(user=other_user, followed_user=user)
        
    def test_user_can_accept_a_follow_request(self):
        self.assertFalse(self.follow.verified)
        
        response = self.client.post(reverse("relations:accept", kwargs={"username": self.follow.user.username}))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        js = response.json()
        self.assertEqual(js["verified"], True)
    
    def test_user_can_not_accept_a_follow_that_does_not_exists(self):
        response = self.client.post(reverse("relations:accept", kwargs={"username": "user"}))
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestFollowingListView(APITestCase):
    def setUp(self) -> None:
        self.user = create_user(username='admin', password='password')
        self.client = APIClient()
        self.client.login(username='admin', password='password')
        return super().setUp()

    def test_user_can_get_a_list_of_followed_users(self):
        self.assertEqual(self.user.following.count(), 0)
        create_follow(self.user, create_user(username="username"))
        create_follow(self.user, create_user(username="username2", private=True))
        
        response = self.client.get(reverse("relations:following", kwargs={"username": self.user.username}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        js = response.json()
        self.assertEqual(len(js["results"]), 2)
        self.assertEqual(self.user.following.count(), 2)
    
    def test_user_can_get_a_list_of_other_user_followed_users(self):
        user = create_user(username="username", password="password")
        
        create_follow(self.user, create_user(username="username1"))
        create_follow(user, create_user(username="username2", private=True))
        
        create_follow(user, create_user(username="username3"))
        
        other = create_user(username="username5", private=True)
        create_follow(self.user, other)
        create_follow(user, other)
        
        response = self.client.get(reverse("relations:following", kwargs={"username": user.username}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        js = response.json()
        self.assertEqual(len(js["results"]), 2)
        
    def test_user_cannot_get_a_list_of_a_private_users_followed_users(self):
        user = create_user(username="username", password="password", private=True)
        
        create_follow(self.user, create_user(username="username1"))
        create_follow(user, create_user(username="username2", private=True))
        
        create_follow(user, create_user(username="username3"))
        
        response = self.client.get(reverse("relations:following", kwargs={"username": user.username}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
class TestFollowersListView(APITestCase):
    def setUp(self) -> None:
        self.user = create_user(username='admin', password='password')
        self.client = APIClient()
        self.client.login(username='admin', password='password')
        return super().setUp()

    def test_user_can_get_a_list_of_his_followers(self):
        create_follow(create_user(username="username"), self.user)
        create_follow(create_user(username="username2", private=True), self.user)
        
        response = self.client.get(reverse("relations:followers", kwargs={"username": self.user.username}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        js = response.json()
        self.assertEqual(len(js["results"]), 2)
    
    
    def test_user_can_get_a_list_of_other_user_followers(self):
        user = create_user(username="username", password="password")
        
        create_follow(create_user(username="username1"), self.user)
        create_follow(create_user(username="username2", private=True), user)
        
        create_follow(create_user(username="username3"), user)
        
        other = create_user(username="username5", private=True)
        
        create_follow(self.user, other)
        create_follow(other, user)
        
        response = self.client.get(reverse("relations:followers", kwargs={"username": user.username}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        js = response.json()
        self.assertEqual(len(js["results"]), 2)
        
    def test_user_cannot_get_a_list_of_a_private_user_followers(self):
        user = create_user(username="username", password="password", private=True)
        
        create_follow(create_user(username="username1"), self.user)
        create_follow(create_user(username="username2", private=True), user)
        
        create_follow(create_user(username="username3"), user)
        
        response = self.client.get(reverse("relations:followers", kwargs={"username": user.username}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)