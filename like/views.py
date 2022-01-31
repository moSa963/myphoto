from django.db.models.aggregates import Count
from api import serializers
from post.models import Post
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status, exceptions

from post.serializers import PostSerializer
from .models import CommentLike, Like
from .serializers import LikeSerializer
from rest_framework.permissions import IsAuthenticated
from post.permissions import post_accessble
from django.db.models import Q

# Create your views here.

class LikeView(GenericAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    #like a post
    def post(self, request, **kwargs):
        post_id = kwargs.get('id', 0)
        user_id = request.user.id
        id = str(user_id) + "-" + str(post_id)

        Like.objects.get_or_create(id=id, user_id=user_id, post_id=post_id)
        return Response(status=status.HTTP_200_OK)

    #delete a like from post
    def delete(self, request, **kwargs):
        post_id = kwargs.get('id', 0)
        user_id = request.user.id
        Like.objects.filter(user_id=user_id, post_id=post_id).delete()
        return Response(status=status.HTTP_200_OK)


class CommentLikeView(GenericAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        comment_id = kwargs.get('id', 0)
        user_id = request.user.id
        id = str(user_id) + "-" + str(comment_id)
        CommentLike.objects.get_or_create(id=id, user_id=user_id, comment_id=comment_id)
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, **kwargs):
        comment_id = kwargs.get('id', 0)
        user_id = request.user.id
        CommentLike.objects.filter(user_id=user_id, comment_id=comment_id).delete()
        return Response(status=status.HTTP_200_OK)

class LikeListView(ListAPIView):
    serializer_class = LikeSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('id', 0)

        if not post_accessble(self.request, Post.objects.get(id=post_id)):
            raise exceptions.NotFound()
        
        if self.request.user.is_authenticated:
            user_id = self.request.user.id
        else:
            user_id = 0
        
        #get users that liked this post
        return Like.objects.filter(
            Q(post_id=post_id),
            Q(user__settings__is_private=False) | Q(user__following__id=user_id)
        )

class PostsLikedView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.request.user

        query = Post.objects.select_related("user").annotate(like=Count("likes", distinct=True),
            comment=Count("comments"), user_liked=Count("likes", filter=Q(likes__user_id=self.request.user.id))
            ).filter(
                (Q(user=self.request.user) | (Q(is_private=False) & 
                (Q(user__is_private=False) | (Q(user__following__user=self.request.user) & Q(user__following__is_verified=True)))))
            ).exclude(user_liked=0)

        sort = self.request.GET.get("sort", "new")
        if sort == "new":
            query = query.order_by('-date')
        elif sort == "old":
            query = query.order_by('date')
        elif sort == "likes":
            query = query.order_by("-like")

        query = query.prefetch_related('images')

        return query
