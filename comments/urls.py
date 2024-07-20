from .views import CommentList, CommentView
from django.urls import path

urlpatterns = [
    path('', CommentView.as_view()),
    path('<int:id>', CommentView.as_view()),
    path('post/<int:post_id>', CommentList.as_view()),
]