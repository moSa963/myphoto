from django.urls import path
from posts import views

app_name = "posts"

urlpatterns = [
    path('<int:id>/image/<str:name>', views.PostImageView.as_view(), name="image"),
    path('<int:id>/likes/', views.PostLikeView.as_view(), name="like"),
    path('<int:id>/likes/list', views.LikeListView.as_view(), name="like_list"),
    path('<int:id>', views.PostView.as_view(), name="show"),
    path('list', views.PostListView.as_view(), name="list"),
    path('list/<str:username>', views.UsersPostsListView.as_view(), name="users_list"),
    path('list/<str:username>/liked', views.UsersLikedPostsListView.as_view(), name="users_liked_list"),
    path('', views.PostCreateView.as_view(), name="create"),
] 