from django.urls import path
from .views import CommentLikeView, LikeListView, LikeView, PostsLikedView

urlpatterns = [
    path('post/<int:id>', LikeView.as_view()),
    path('comment/<int:id>', CommentLikeView.as_view()),
    path('list', LikeListView.as_view()),
    path('post/list', PostsLikedView.as_view()),
]