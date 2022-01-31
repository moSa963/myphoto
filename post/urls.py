from django.urls import path, include
from .views import PostView, PostImageView, PostList

urlpatterns = [
    path('image/<int:id>', PostImageView.as_view()),
    path('<int:id>', PostView.as_view()),
    path('list', PostList.as_view()),
    path('', PostView.as_view()),
]