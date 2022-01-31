from django.urls import path
from django.urls.conf import include
from .views import Register, Login, UserImageView, UserList, UserView, ProfileView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register', Register.as_view()),
    path('login', Login.as_view()),
    path('token/refresh', TokenRefreshView.as_view()),
    path('user', ProfileView.as_view()),
    path('user/<str:username>', UserView.as_view()),
    path('user/image/<str:username>', UserImageView.as_view()),
    path('user/list/<str:key>', UserList.as_view()),
    path('post/', include('post.urls')),
    path('follow/', include('follow.urls')),
    path('history/', include('history.urls')),
    path('comment/', include('comment.urls')),
    path('like/', include('like.urls')),
]