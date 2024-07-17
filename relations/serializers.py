from rest_framework import serializers
from users.models import User
from users.serializers import UserSerializer
from relations.models import Follow

class FollowSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    followed_user = UserSerializer(read_only=True)
    
    user_id = serializers.IntegerField(required=True, write_only=True)
    followed_user_id = serializers.IntegerField(required=True, write_only=True)
    
    verified = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Follow
        fields=("user", "followed_user", "verified", "created_at", "user_id", "followed_user_id")
        
    def create(self, validated_data):
        user_id = validated_data.get("user_id")
        followed_user_id = validated_data.get("followed_user_id")
        
        if user_id == followed_user_id:
            raise serializers.ValidationError({"user": "A user could not follow himself."})
        
        follow,_ = Follow.objects.get_or_create(user_id=user_id, followed_user_id=followed_user_id)
        
        if follow.verified:
            return follow
    
        followed_user = User.objects.get(pk=followed_user_id)
        
        if not followed_user.private:
            follow.verified = True
            follow.save()
            
        return follow