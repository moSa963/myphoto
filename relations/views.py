from django.shortcuts import render
from rest_framework.generics import GenericAPIView, ListAPIView
from relations.serializers import FollowSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from users.models import User
from django.db.models import Q
from relations.permissions import is_user_accessible
# Create your views here.


class FollowView(GenericAPIView):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        following = get_object_or_404(get_user_model(), username=kwargs["username"])
        
        serializer =  self.get_serializer(data={
            "user_id": request.user.id,
            "followed_user_id": following.id,
        })
        
        serializer.is_valid(raise_exception=True)
        
        serializer.save()
        
        return Response(data=serializer.data)

        
    def delete(self, request, *args, **kwargs):
        request.user.following.filter(followed_user__username=kwargs["username"]).delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class AcceptFollowView(GenericAPIView):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        follow = request.user.followers.filter(user__username=kwargs["username"]).first()
        
        if not follow:
            raise Http404()
        
        follow.set_verified()
        
        return Response(self.get_serializer(instance=follow).data)

class FollowingListView(ListAPIView):
    serializer_class = FollowSerializer
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        user = get_object_or_404(get_user_model(), username=self.kwargs["username"])
        auth = self.request.user
        
        is_user_accessible(self.request, user)
        
        query = user.following

        if user.id != auth.id:
            query = query.filter(Q(followed_user__private=False) | (Q(followed_user__followers__user_id=auth.id) & Q(followed_user__followers__verified=True)))
            
        return query

    
class FollowersListView(ListAPIView):
    serializer_class = FollowSerializer
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        user = get_object_or_404(get_user_model(), username=self.kwargs["username"])
        auth = self.request.user

        is_user_accessible(self.request, user)
        
        query = user.followers
        
        if user.id != auth.id:
            query = query.filter(Q(user__private=True) | (Q(user__followers__user_id=auth.id) & Q(user__followers__verified=True)))
        
        return query