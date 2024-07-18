from .views import FollowView, AcceptFollowView, FollowingListView, FollowersListView
from django.urls import path


app_name = "relations"

urlpatterns = [
    path('<str:username>', FollowView.as_view(), name="follow"),
    path('accept/<str:username>', AcceptFollowView.as_view(), name="accept"),
    path('<str:username>/following/list', FollowingListView.as_view(), name="following"),
    path('<str:username>/followers/list', FollowersListView.as_view(), name="followers"),
]
    