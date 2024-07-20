from django.urls import path
from .views import PostView, PostCreateView, PostImageView, PostListView, PostLikeView, LikeListView

app_name = "posts"

urlpatterns = [
    path('<int:id>/image/<str:name>', PostImageView.as_view(), name="image"),
    path('<int:id>/likes/', PostLikeView.as_view(), name="like"),
    path('<int:id>/likes/list', LikeListView.as_view(), name="like_list"),
    path('<int:id>', PostView.as_view(), name="show"),
    path('list', PostListView.as_view(), name="list"),
    path('', PostCreateView.as_view(), name="create"),
] 