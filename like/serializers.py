from rest_framework import serializers
from api.serializers import UserSerializer
from .models import Like

class LikeSerializer(serializers.Serializer):
    user = UserSerializer()
    post_id = serializers.IntegerField()

    class Meta:
        model = Like
        fields = ['user', 'post_id']