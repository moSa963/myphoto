from django.shortcuts import render
from rest_framework.generics import GenericAPIView, ListAPIView
from comments.models import PostComment, CommentLike
from comments.serializers import CommentSerializer, CommentLikeSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from posts.models import Post
from rest_framework import status
from rest_framework.response import Response
from comments.permissions import is_owner
from posts.permissions import is_post_accessible
from django.db.models import Count, Q, Exists, OuterRef
# Create your views here.


class CommentCreateView(GenericAPIView):
    serializer_class=CommentSerializer
    permission_classes=[IsAuthenticated]
    
    def post(self, request, **kwargs):
        post = get_object_or_404(Post, id=kwargs["post_id"])
        
        is_post_accessible(request, post)
        
        comment = self.get_serializer(data={
            "user_id": request.user.id,
            "post_id": post.id,
            "content": request.data.get("content")
        })
        
        comment.is_valid(raise_exception=True)
        comment.save()
        
        return Response(data=comment.data, status=status.HTTP_201_CREATED)
        

class CommentDeleteView(GenericAPIView):
    serializer_class=CommentSerializer
    permission_classes=[IsAuthenticated]
    
    def delete(self, request, **kwargs):
        post = get_object_or_404(Post, id=kwargs["post_id"])
        comment = get_object_or_404(PostComment, post_id=post.id, id=kwargs["id"])
        
        is_owner(request, comment)
        
        comment.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CommentListView(ListAPIView):
    serializer_class=CommentSerializer
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        
        is_post_accessible(self.request, post)
        
        q = post.comments.annotate(
            likes_count=Count("likes"), liked=Exists(CommentLike.objects.filter(comment_id=OuterRef("pk"), user_id=self.request.user.id))
        )
        
        return q
    
    
class CommentLikeView(GenericAPIView):
    serializer_class=CommentLikeSerializer
    permission_classes=[IsAuthenticated]
    
    def post(self, request, **kwargs):
        post = get_object_or_404(Post, id=kwargs['post_id'])
        is_post_accessible(request, post)
        
        comment = get_object_or_404(post.comments, id=kwargs['id'])
        
        serializer = self.get_serializer(data={
            "user_id": request.user.id,
            "comment_id": comment.id,
        })

        serializer.is_valid(raise_exception=True)        
        serializer.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def delete(self, request, **kwargs):
        post = get_object_or_404(Post, id=kwargs['id'])
        
        like = request.user.comments_likes.filter(comment__post_id=post.id).first()

        if like:
            like.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)