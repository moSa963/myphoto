from django.urls import path
from .views import Register, User, Login, AuthUser, UserImageView, UsersList
from rest_framework_simplejwt.views import TokenRefreshView

app_name = "users"

urlpatterns = [
    path('', AuthUser.as_view(), name="user"),
    path('login/', Login.as_view(), name="login"),
    path('token/refresh', TokenRefreshView.as_view()),
    path('register/', Register.as_view(), name="register"),
    path('list', UsersList.as_view()),
    path('<str:username>', User.as_view()),
    path('<str:username>/image', UserImageView.as_view()),
]
