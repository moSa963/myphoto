from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model

class TestLoginView(APITestCase):

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(username="admin", password="password")
        self.client = APIClient()
        
    def test_user_can_login(self):
        data = {
            "username": "admin",
            "password": "password"
        }

        response = self.client.post(reverse("users:login"), data=data)
        self.assertEqual(response.status_code, 200)
        
        js = response.json()
        self.assertEqual(js["user"]["username"], "admin")
        self.assertTrue(js["refresh"] != None)
        self.assertTrue(js["access"] != None)


class TestRegisterView(APITestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_user_can_register(self):

        data = {
            "username": "admin",
            "first_name": "firstname",
            "last_name": "lastname",
            "password": "password",
            "password_confirmation": "password",
            "email": "admin@yahoo.com"
        }

        response = self.client.post(reverse("users:register"), data=data)
        self.assertEqual(response.status_code, 201)
        
        js = response.json()
        self.assertEqual(js["user"]["username"], "admin")
        self.assertTrue(js["refresh"] != None)
        self.assertTrue(js["access"] != None)

