from django.shortcuts import render
from rest_framework.generics import GenericAPIView, ListAPIView
from .serializers import UserCreateSerializer, UserSerializer, LoginSerializer, UserUpdateSerializer
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework_simplejwt import tokens
from .models import User as UserModel
from django.shortcuts import get_object_or_404
from django.http.response import FileResponse
from rest_framework import status 

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
        user = get_object_or_404(UserModel, username=kwargs['username'])
        serializer = UserSerializer(instance=user)
        return Response(serializer.data)

class UserImageView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, **kwargs):
        user = get_object_or_404(UserModel, username=kwargs['username'])
        return FileResponse(open(user.image.path, 'rb'))

class UsersList(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        key = self.request.GET.get('key', '')

        query = UserModel.objects.filter(username__icontains=key)

        return query