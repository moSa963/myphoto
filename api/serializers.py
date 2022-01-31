from os import read, write
from django.db.models import fields
from rest_framework import serializers
from .models import UserProfile
from rest_framework import authentication

from api import models

class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(min_length=3, max_length=30)
    last_name =  serializers.CharField(min_length=3, max_length=30)
    username =   serializers.RegexField(regex=r'^[a-zA-Z]+([._-]?[a-zA-Z0-9]+)+$', min_length=3, max_length=30)
    email =      serializers.EmailField(min_length=5, write_only=True)
    password =   serializers.CharField(min_length=8, max_length=50, write_only=True)
    is_private =   serializers.BooleanField(read_only=True, default=False)
    is_verified =  serializers.BooleanField(read_only=True, default=False)
    image = serializers.ImageField(required=False, write_only=True)
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    is_following = serializers.BooleanField(read_only=True, default=None)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'is_private', 'is_verified', 'image', 'followers_count', 'following_count', 'is_following'] 

    def to_representation(self, instance):
        old = super().to_representation(instance)
        return old

    def create(self, validated_data):
        user = UserProfile.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        instance.is_private = validated_data.get("is_private", instance.is_private)
        instance.image = validated_data.get("image", instance.image)
        return instance

class RegisterSerializer(UserSerializer):
        password_confirmation = serializers.CharField(min_length=8, max_length=50, write_only=True)

        class Meta:
            model = UserProfile
            fields = ['first_name', 'last_name', 'username', 'email', 'password', 'is_private', 'is_verified', 'image', 'password_confirmation']

        def validate(self, attrs):
            if attrs['password'] != attrs['password_confirmation']:
                raise serializers.ValidationError({'password': ('password is not confurmed.')})

            attrs.pop("password_confirmation")

            if UserProfile.objects.filter(username=attrs['username']).exists():
                raise serializers.ValidationError({'username': ('username most be unique')})

            if UserProfile.objects.filter(email=attrs['email']).exists():
                raise serializers.ValidationError({'email': ('email most be unique')})

            return super().validate(attrs)

        def create(self, validated_data):
            user = UserProfile.objects.create_user(**validated_data)
            return user


class LoginSerializer(serializers.Serializer):
    username = serializers.RegexField(regex=r'^[a-zA-Z]+([._-]?[a-zA-Z0-9]+)+$', min_length=3, max_length=30)
    password = serializers.CharField(min_length=8, max_length=50, write_only=True)

    class Meta:
        fields = ['username', 'password']

    def create(self, validated_data):
        return authentication.authenticate(**validated_data)


class UserUpdate(serializers.Serializer):
    image = serializers.ImageField(required=False, write_only=True, allow_empty_file=False, allow_null=False)
    is_private =  serializers.BooleanField(required=False)

    class Meta:
        model = UserProfile
        fields = ['is_private', 'image']

    def update(self, instance, validated_data):
        instance.is_private = validated_data.get("is_private", instance.is_private)
        instance.image = validated_data.get("image", instance.image)
        instance.save()
        return instance