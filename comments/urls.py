from django.urls import path
from comments.views import CommentCreateView, CommentListView, CommentDeleteView, CommentLikeView

app_name = "comments"

urlpatterns = [
    path('', CommentCreateView.as_view(), name="create"),
    path('<int:id>', CommentDeleteView.as_view(), name="delete"),
    path('list', CommentListView.as_view(), name="list"),
    path('<int:id>/likes', CommentLikeView.as_view(), name="like"),
] 