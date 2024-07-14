from rest_framework import serializers
from .models import Post, PostImage
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
    
    class Meta:
        model = Post
        fields = ("user", "title", "description", "private", "created_at", "images")
    
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
        