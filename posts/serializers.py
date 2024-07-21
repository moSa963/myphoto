from rest_framework import serializers
from .models import Post, PostImage, PostLike
from users.serializers import UserSerializer

class PostImageSerializer(serializers.ModelSerializer):
    post_id = serializers.IntegerField(write_only=True)
    image = serializers.ImageField(write_only=True, required=True)
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = PostImage
        fields=("post_id", "image", "url")
    
    def get_url(self, obj):
        return f"/posts/{obj.post_id}/image/{obj.image.name.split('/')[-1]}"
    
    def create(self, validated_data):
        post_id = validated_data.get('post_id')
        image = validated_data.get('image')
        
        post_image = PostImage(post_id=post_id, image=image)
        post_image.save()
        return post_image

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    title = serializers.CharField(max_length=50, default='')
    description = serializers.CharField(default="")
    private = serializers.BooleanField(default=True)
    images = PostImageSerializer(many=True, read_only=True)
    
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    liked = serializers.BooleanField(read_only=True)
        
    class Meta:
        model = Post
        fields = ("user", "title", "description", "private", "created_at", "images", "likes_count", "liked", "comments_count")

    def to_representation(self, instance):
        json = super().to_representation(instance)
        
        if json.get("likes_count", None) == None:
            json['likes_count'] = self.get_likes_count(instance)
        
        if json.get("comments_count", None) == None:
            json['comments_count'] = self.get_comments_count(instance)
            
        if json.get("liked", None) == None:
            json['liked'] = self.get_liked(instance)
        
        return json
        
        
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def get_liked(self, obj):
        user = self.context.get('user')
        
        if not user:
            return False
        
        return obj.likes.filter('user_id', user.id).exists()
    
    def create(self, validated_data):
        request = self.context['request']
        title = validated_data.get('title')
        description = validated_data.get('description')
        private = validated_data.get('private')
        images = request.FILES.getlist('images')
        
        if not images or len(images) <= 0:
            raise serializers.ValidationError({"images": "images should have at least one file."})
        elif len(images) > 5:
            raise serializers.ValidationError({"images": "Maximum number of images is 5."})
        
        post = Post(title=title, description=description, private=private, user=request.user)
        post.save()
        
        for image in images:
            serializer = PostImageSerializer(data={
                "image": image,
                "post_id": post.id
            })
            
            if not serializer.is_valid():
                post.delete()
                raise serializers.ValidationError()
            serializer.save()
        
        return post


class PostLikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post_id = serializers.IntegerField()
    
    user_id = serializers.IntegerField(write_only=True)
    
    created_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model=PostLike
        fields=("user", "user_id", "post_id", "created_at")
        
    def create(self, validated_data):
        user_id = validated_data["user_id"]
        post_id = validated_data["post_id"]

        like = PostLike.objects.get_or_create(user_id=user_id, post_id=post_id)
        
        return like