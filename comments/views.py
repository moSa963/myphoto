from django.db.models.aggregates import Count
from django.db.models.query_utils import Q
from comment.models import Comment
from rest_framework import status
from rest_framework.response import Response
from .serializers import CommentSerializer
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

# Create your views here.

class CommentView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def post(self, request, **kwargs):
        comment = self.get_serializer(data=request.data)
        comment.is_valid(raise_exception=True)
        comment.save()
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, **kwargs):
        try:
            comment = Comment.objects.get(id=kwargs["id"])
            if comment and comment.user_id == request.user.id:
                comment.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

class CommentList(ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        query = Comment.objects.filter(post_id=self.kwargs.get("post_id")
                    ).annotate(like=Count("likes"), user_liked=Count("likes", filter=Q(likes__user__id=1)))

        sort = self.request.GET.get("sort", "")
        if sort == "new":
            query = query.order_by('-date')
        elif sort == "old":
            query = query.order_by('date')
        elif sort == "likes":
            query = query.order_by("-like")
        return query