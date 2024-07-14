from django.contrib.auth.models import User
from django.db.models import fields
from rest_framework import request, serializers
from .models import Post, Image
from api.serializers import UserSerializer

class ImageSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    post_id = serializers.IntegerField(write_only=True)
    image = serializers.ImageField(write_only=True)

    def to_representation(self, instance):
        d = super().to_representation(instance)
        d.update({'url': '/api/post/image/' + str(d.get('id'))})
        return d
        
    class Meta:
        model = Image
        fields = ['post_id', 'image']

    def create(self, validated_data):
        return Image.objects.create(**validated_data)



class PostSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user = UserSerializer(read_only=True)
    title = serializers.CharField(max_length=50, default='')
    description = serializers.CharField(max_length=300, default='')
    is_private = serializers.BooleanField(default=True)
    images = ImageSerializer(many=True, read_only=True)
    date = serializers.DateTimeField(read_only=True)
    likes = serializers.IntegerField(source="like", read_only=True)
    user_liked = serializers.BooleanField(read_only=True, default=False)
    comment = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = ['title', 'description', 'is_private']

    def validate(self, attrs):
        #make sure there is 1 or at most 5 images
        request = self.context.get("request")
        img_list = request.FILES.getlist('image')
        if len(img_list) > 5 or len(img_list) <= 0:
            raise serializers.ValidationError({'image': ('post must have atleast 1 image and atmost 5.')})

        return super().validate(attrs)

    def create(self, validated_data):
        request = self.context.get("request")

        post = Post.objects.create(user_id=request.user.id, **validated_data)

        img_list = request.FILES.getlist('image')
        images = []
        #add post imges
        if post:
            for img in img_list:
                try:
                    ser = ImageSerializer(data={'post_id': post.id, 'image': img})
                    ser.is_valid(raise_exception=True)
                    images.append(ser)
                except Exception as e:
                    #if the image is not valid delete the post and raise the exception
                    post.delete()
                    raise e

        for img in images:
            img.save()

        return post

    def update(self, instance, validated_data):
        instance.is_private = validated_data.get("is_private", instance.is_private)
        instance.save()
        return instance

    def __str__(self) -> str:
        return self.title


class PostUpdate(serializers.Serializer):
    is_private =  serializers.BooleanField(required=False)

    class Meta:
        model = Post
        fields = ['is_private']

    def update(self, instance, validated_data):
        instance.is_private = validated_data.get("is_private", instance.is_private)
        instance.save()
        return instance