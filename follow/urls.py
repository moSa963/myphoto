from .views import FollowView, FollowersListView, FollowingListView
from django.urls import path


urlpatterns = [
    path('following/<str:username>', FollowingListView.as_view()),
    path('followers/<str:username>', FollowersListView.as_view()),
    path('accept/<str:id>', FollowView.as_view()),
    path('<str:username>', FollowView.as_view()),
]
