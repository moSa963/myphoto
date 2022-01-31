from django.urls import path
from .views import CommentHistory, HistoryPostList, HistoryLikeList

urlpatterns = [
    path("list", HistoryPostList.as_view()),
    path("like", HistoryLikeList.as_view()),
    path("comment", CommentHistory.as_view()),
]
