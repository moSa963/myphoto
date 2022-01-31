from django.db.models.aggregates import Count
from django.db.models.functions import Coalesce
from history.serializers import CommentHistorySerializer
from django.db.models.expressions import F
from django.db.models.query_utils import Q
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from post.serializers import PostSerializer
from post.models import Post
# Create your views here.


class HistoryPostList(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def get_queryset(self):
        query = Post.objects.filter(Q(watched__user__id = self.request.user.id),
        Q(user=self.request.user) | (Q(is_private=False)  & (Q(user__is_private=False)  |
        (Q(user__following__user=self.request.user) & Q(user__following__is_verified=True))))
        ).annotate(like=Count("likes"), user_liked=Count("likes", filter=Q(likes__user_id=self.request.user.id))).order_by("-watched__date")
        return query

class HistoryLikeList(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def get_queryset(self):
        query = Post.objects.filter(likes__user__id=self.request.user.id
        ).annotate(like=Count("likes"), user_liked=Count("likes", filter=Q(likes__user_id=self.request.user.id))).order_by("-likes__date")
        return query

class CommentHistory(ListAPIView):
    serializer_class = CommentHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.comments.annotate(
            post_title=F("post__title"), like=Count("likes"), user_liked=Count("likes", filter=Q(likes__user_id=self.request.user.id)),
            reply_to_text=Coalesce(F('reply_to__text'), None),
            reply_to_username=Coalesce(F('reply_to__user__username'), None),
            reply_to_date=F('reply_to__date'),
        ).order_by("-date").all()