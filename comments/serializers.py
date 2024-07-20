from django.db.models.aggregates import Count
from django.db.models.query_utils import Q
from comment.models import Comment
from api.serializers import UserSerializer
from rest_framework import serializers

class CommentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user = UserSerializer(read_only=True)
    post_id = serializers.IntegerField()
    content = serializers.CharField(max_length=1000)
    date = serializers.DateTimeField(read_only=True)
    user_liked = serializers.IntegerField(read_only=True)
    likes = serializers.IntegerField(source="like", read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post_id', "content", 'date']
        
    def create(self, validated_data):
        comment = Comment(user_id=self.context["request"].user.id,  **validated_data)
        comment.save()
        return comment
