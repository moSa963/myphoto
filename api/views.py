from functools import partial
from django.db.models.expressions import F, Case, When
from django.db.models.fields import BooleanField
from django.db.models.query_utils import Q
from django.http.response import FileResponse
from django.shortcuts import render
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework import status
from .serializers import LoginSerializer, RegisterSerializer, UserUpdate
from rest_framework_simplejwt import tokens
from django.db.models.aggregates import Count
from .models import UserProfile
from rest_framework.response import Response
from .serializers import UserSerializer
from api import models
from rest_framework.permissions import IsAuthenticated
from .permissions import is_user_accessble
# Create your views here.

class Register(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()

        refresh_token = tokens.RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh_token),
            'access': str(refresh_token.access_token)}, status=status.HTTP_200_OK)


class Login(GenericAPIView):
    serializer_class = LoginSerializer

    #get the authenticated user
    def get(self, request):
        if request.user.is_authenticated:
            user = UserProfile.objects.annotate(
                followers_count=Count("followers", filter=Q(followers__is_verified=True)), followed_count=Count("following", filter=Q(following__is_verified=True))
                ).get(id=request.user.id)

            return Response(data=UserSerializer(user).data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_401_UNAUTHORIZED)

    #login
    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid()
        try:
            user = ser.save()
            refresh_token = tokens.RefreshToken.for_user(user)

            user = UserProfile.objects.annotate(
                followers_count=Count("followers", filter=Q(followers__is_verified=True)), followed_count=Count("following", filter=Q(following__is_verified=True))
                ).get(id=user.id)

            return Response({'user': UserSerializer(user).data,
             'refresh': str(refresh_token),
             'access': str(refresh_token.access_token)}, status=status.HTTP_200_OK)
        except:
            return Response({"username": ['username or password are wrong',],}, status=status.HTTP_400_BAD_REQUEST)


class UserImageView(GenericAPIView):

    def get(self, requset, **kwargs):
        username = kwargs.get('username', 0)
        try:
            user = UserProfile.objects.get(username=username)
            return FileResponse(open(str(user.image), 'rb'))
        except:
            return FileResponse(open('media/img/default/user.png', 'rb'))


class UserList(ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        key = self.kwargs.get('key', 0)
        user_id = self.request.user.id

        return UserProfile.objects.filter(username__icontains=key
            ).exclude(id=user_id).annotate(followers_count=Count("followers"), followed_count=Count("following"),
            is_following=Case(
                When(followers__user__id=user_id, then=F("followers__is_verified")),
                output_field=BooleanField(null=True)
            )
        )


class UserView(GenericAPIView):
    serializer_class = UserSerializer

    def get(self, request, **kwargs):
        username = kwargs.get("username", "")
        user_id = getattr(request.user, "id", 0)

        user = UserProfile.objects.filter(username=username
        ).annotate(followers_count=Count("followers", filter=Q(followers__is_verified=True)),
         following_count=Count("following", filter=Q(following__is_verified=True)),
         is_following=Case(
             When(followers__user__id=user_id, then=F("followers__is_verified")),
             output_field=BooleanField(null=True)
         )).first()

        userSer = self.get_serializer(user)

        return Response(data=userSer.data, status=status.HTTP_200_OK)



class ProfileView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdate

    def put(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)