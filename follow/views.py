from django.db.models.expressions import F, Case, When
from django.db.models.fields import BooleanField
from django.db.models.query_utils import Q
from api.models import UserProfile
from follow.serializers import FollowSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Follow
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from api.permissions import is_user_accessble
from rest_framework.exceptions import NotAuthenticated, NotFound
# Create your views here.

class FollowView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowSerializer

    #follow a user
    def post(self, request, **kwargs):
        try:
            username = kwargs.get('username', 0)
            following = UserProfile.objects.filter(username=username).first()
            id = str(request.user.id) + "-" + str(following.id)
            
            follow, u = Follow.objects.get_or_create(id=id, defaults={"user_id": request.user.id, "following_id": following.id})

            #if the user that getting followed not private make the request accepted "verified"
            if not following.is_private:
                Follow.objects.filter(id=follow.id).update(is_verified=True)

            follow = self.get_serializer(Follow.objects.get(id=follow.id))
            return Response(data=follow.data, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'username is wrong or not exists'}, status=status.HTTP_404_NOT_FOUND)
        

    #unfollow a user
    def delete(self, request, **kwargs):
        try:
            following_username = kwargs.get('username', 0)
            UserProfile.objects.get(username=kwargs.get('username', 0))
            Follow.objects.filter(user=request.user, following__username=following_username).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({'message': 'username is wrong or does not exist'}, status=status.HTTP_404_NOT_FOUND)


    #accept a follow request
    def put(self, request, **kwargs):
        id = kwargs.get("id", None)

        try:                
            follow = Follow.objects.get(id=id)

            #the requested user should be the same user that getting followed
            if not follow.following_id == request.user.id:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

            Follow.objects.filter(id=id).update(is_verified=True)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)



class FollowingListView(ListAPIView):
    serializer_class = FollowSerializer
    
    def get_queryset(self):
        username = self.kwargs.get('username', None)
        user = UserProfile.objects.get(username=username)

        if not user or not is_user_accessble(self.request, user):
            raise NotAuthenticated(detail={"message": "user is not accessble"})

        key = self.request.GET.get("key", None)

        query = Follow.objects.filter(user_id=user.id, is_verified=True )
        if key:
            query = query.filter(Q(following__username__icontains=key) | Q(following__first_name__icontains=key) | Q(following__last_name__icontains=key))

        return query



class FollowersListView(ListAPIView):
    serializer_class = FollowSerializer

    def get_queryset(self):
        username = self.kwargs.get('username', None)
        user = UserProfile.objects.filter(username=username).first()

        if not user or not is_user_accessble(self.request, user):
            raise NotAuthenticated(detail={"message": "user is not accessble"})

        unverified = self.request.GET.get("unverified", None)

        if unverified and unverified == "true":
            if user.username == self.request.user.username:
                return Follow.objects.filter(following_id=self.request.user.id, is_verified=False).select_related()
            else:
                raise NotFound()
        
        key = self.request.GET.get("key", None)

        query = Follow.objects.filter(following_id=user.id, is_verified=True)
        if key:
            query = query.filter(Q(following_id=user.id), Q(is_verified=True) and (Q(user__username__icontains=key) | Q(user__first_name__icontains=key) | Q(user__last_name__icontains=key)))

        return query

