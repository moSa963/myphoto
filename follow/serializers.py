from rest_framework import serializers
from api.serializers import UserSerializer
from .models import Follow

class FollowSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    user = UserSerializer()
    following = UserSerializer()
    is_verified = serializers.BooleanField(read_only=True)
    following_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Follow
        fields = ['user', 'following', 'is_verified', 'following_date']
