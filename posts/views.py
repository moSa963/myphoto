from django.shortcuts import render
from rest_framework.generics import GenericAPIView, ListAPIView
from .serializers import PostSerializer, PostLikeSerializer
from .permissions import IsOwnerOrReadOnly, is_post_accessible
from rest_framework.permissions import IsAuthenticated
from .models import Post, PostLike
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404, FileResponse

# Create your views here.
class PostView(GenericAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrReadOnly]
    
    def get(self, request, **kwargs):
        id = kwargs.get('id', 0)
        serializer = PostSerializer(instance=get_object_or_404(Post, id=id))

        return Response(serializer.data)

    def delete(self, request, **kwargs):
        id = kwargs.get('id', 0)
        post = Post.objects.get(id=id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PostCreateView(GenericAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PostListView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        query = Post.objects.related_posts(self.request.user, self.request.GET.get("sort", "new"))
        return query

class PostImageView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        post = get_object_or_404(Post, id=kwargs['id'])

        image = post.images.filter(image__endswith="/" + kwargs['name']).first()
        
        if not image:
            raise Http404()
        
        return FileResponse(open(image.image.path, 'rb'))


class PostLikeView(GenericAPIView):
    serializer_class=PostLikeSerializer
    permission_classes=[IsAuthenticated]
    
    def post(self, request, **kwargs):
        post = get_object_or_404(Post, id=kwargs['id'])
        
        is_post_accessible(request, post)
        
        serializer = self.get_serializer(data={
            "user_id": request.user.id,
            "post_id": post.id,
        })

        serializer.is_valid(raise_exception=True)        
        serializer.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def delete(self, request, **kwargs):
        post = get_object_or_404(Post, id=kwargs['id'])
        
        like = PostLike.objects.filter(user_id=request.user.id, post_id=post.id).first()

        if like:
            like.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class LikeListView(ListAPIView):
    serializer_class=PostLikeSerializer
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs['id'])
        
        is_post_accessible(self.request, post)
        
        q = post.likes.related_likes(self.request.user)
        
        return q