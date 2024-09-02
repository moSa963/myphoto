from rest_framework import serializers
from comments.models import PostComment, CommentLike
from users.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    post_id = serializers.IntegerField()
    content = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    
    likes_count = serializers.IntegerField(read_only=True)
    liked = serializers.BooleanField(read_only=True)
    
    class Meta:
        model=PostComment
        fields=("id", "user", "user_id", "post_id", "created_at", "content", "likes_count", "liked")
    
    def to_representation(self, instance):
        json = super().to_representation(instance)
        
        if json.get("likes_count", None) == None:
            json['likes_count'] = self.get_likes_count(instance)
        
        if json.get("liked", None) == None:
            json['liked'] = self.get_liked(instance)
            
        return json
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_liked(self, obj):
        request = self.context.get("request")
        
        if not request or not request.user:
            return False
        
        return obj.likes.filter(user_id=request.user.id).exists()
    
    def create(self, validated_data):
        user = validated_data["user_id"]
        post = validated_data["post_id"]
        content = validated_data["content"]
        
        comment = PostComment.objects.create(
            user_id=user,
            post_id=post,
            content=content
        )
        
        return comment
        


class CommentLikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    comment_id = serializers.IntegerField()
    
    user_id = serializers.IntegerField(write_only=True)
    
    created_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model=CommentLike
        fields=("user", "user_id", "comment_id", "created_at")
        
    def create(self, validated_data):
        user_id = validated_data["user_id"]
        comment_id = validated_data["comment_id"]

        like = CommentLike.objects.get_or_create(user_id=user_id, comment_id=comment_id)
        
        return like