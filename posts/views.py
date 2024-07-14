from django.db.models.query_utils import Q
from rest_framework.exceptions import NotAuthenticated, NotFound
from post.utils import delete_post_images
from post.serializers import PostSerializer, PostUpdate
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import Image, Post
from django.http import FileResponse, request
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .permissions import post_accessble
from history.utils import add_to_post_history
from django.db.models import Count


#post view
class PostView(GenericAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    #get post
    def get(self, request, **kwargs):
        id = kwargs.get('id', 0)
        try:
            post = Post.objects.annotate(like=Count(
                "likes"), comment=Count("comments")).get(id=id)
            serializer = self.get_serializer(post)

            if post_accessble(request, post):
                add_to_post_history(request, post)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    #create a post
    def post(self, request):
        #create post
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        return Response({"id": post.id}, status=status.HTTP_201_CREATED)

    def put(self, request, **kwargs):
        id = kwargs.get("id", 0)
        post = Post.objects.get(id=id)

        if post.user_id != request.user.id:
            raise NotFound()

        post = PostUpdate(post, data=request.data, partial=True)
        post.is_valid(raise_exception=True)
        post.save()
        return Response(data=post.data, status=status.HTTP_200_OK)

    #delete a post
    def delete(self, request, **kwargs):
        id = kwargs.get('id', 0)
        post = Post.objects.get(id=id)
        delete_post_images(post)
        post.delete()
        return Response(status=status.HTTP_200_OK)


class PostImageView(GenericAPIView):
    serializer_class = Image

    def get(self, request, **kwargs):
        id = kwargs.get('id', 0)

        try:
            img = Image.objects.get(id=id)
            post = Post.objects.get(id=img.post_id)
            if post_accessble(request, post):
                return FileResponse(open(str(img.image), 'rb'))
        except:
            raise NotFound()
        raise NotAuthenticated()


class PostList(ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        query = ""
        user_id = self.request.user.id

        if self.request.user.is_authenticated:
            query = Post.objects.select_related("user").annotate(like=Count("likes", distinct=True), comment=Count("comments"), user_liked=Count("likes", filter=Q(likes__user_id=user_id))).filter(
                    Q(user_id=user_id) | ( Q(is_private=False) & ( Q(user__is_private=False) | ( Q(user__followers__user_id=user_id) & Q(user__followers__is_verified=True) ) ))
                ).prefetch_related('images')
        else:
            query = Post.objects.select_related("user").annotate(like=Count("likes", distinct=True), comment=Count(
                "comments")).filter(Q(is_private=False) & Q(user__is_private=False)).prefetch_related('images')

        username = self.request.GET.get("user", None)
        if username:
            query = query.filter(user__username=username)

        sort = self.request.GET.get("sort", "new")
        if sort == "new":
            query = query.order_by('-date')
        elif sort == "old":
            query = query.order_by('date')
        elif sort == "likes":
            query = query.order_by("-like")

        return query
