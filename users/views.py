from django.shortcuts import render
from rest_framework.generics import GenericAPIView, ListAPIView
from .serializers import UserCreateSerializer, UserSerializer, LoginSerializer, UserUpdateSerializer, UserListSerializer
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework_simplejwt import tokens
from django.shortcuts import get_object_or_404
from django.http.response import FileResponse
from rest_framework import status 
from django.contrib.auth import get_user_model

class AuthUser(GenericAPIView):
    serializer_class=UserSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(instance=request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserUpdateSerializer(instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=UserSerializer(instance=request.user).data)

class Register(GenericAPIView):
    serializer_class=UserCreateSerializer
    permission_classes=[permissions.AllowAny]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh_token = tokens.RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh_token),
            'access': str(refresh_token.access_token)}, status=status.HTTP_201_CREATED)

class Login(GenericAPIView):
    serializer_class=LoginSerializer
    permission_classes=[permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh_token = tokens.RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh_token),
            'access': str(refresh_token.access_token)})
    
class User(GenericAPIView):
    serializer_class=UserSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get(self, request, **kwargs):
        user = get_object_or_404(get_user_model(), username=kwargs['username'])
        serializer = UserSerializer(instance=user)
        return Response(serializer.data)

class UserImageView(GenericAPIView):
    def get(self, request, **kwargs):
        user = get_object_or_404(get_user_model(), username=kwargs['username'])

        path = "media/defaults/user.png"
        
        if user.image:
            path = user.image.path
            
        return FileResponse(open(path, 'rb'))

class UsersList(ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        key = self.request.GET.get('key', '')

        query = get_user_model().objects.for_user(self.request.user, key)

        return query