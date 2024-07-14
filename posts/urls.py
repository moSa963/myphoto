from django.urls import path, include
from .views import PostView, PostCreateView, PostImageView

app_name = "posts"

urlpatterns = [
    path('<int:id>/image/<str:name>', PostImageView.as_view(), name="image"),
    path('<int:id>', PostView.as_view(), name="show"),
    path('', PostCreateView.as_view(), name="create"),
]