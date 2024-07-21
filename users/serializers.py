from rest_framework import serializers
from .models import User
from rest_framework import authentication


class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField(read_only=True)
    following_count = serializers.SerializerMethodField(read_only=True)
    following_status = serializers.SerializerMethodField(read_only=True)
    
    def get_followers_count(self, obj):
        return obj.followers.count()
    
    def get_following_count(self, obj):
        return obj.following.count()

    
    def get_following_status(self, obj):
        user = self.context.get('user')
        
        if not user:
            return None
        
        return obj.followers.filter(user_id=user.id, verified=True).exists()
    
    class Meta:
        model=User
        fields=["username", "first_name", "last_name", "email", "private", "verified", "followers_count", "following_count", "following_status"]
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        
        if not request or request.user != instance:
            representation.pop("verified")
            representation.pop("email")

        return representation
        
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=["username", "first_name", "last_name","private", "following_status", "followers_count"]
    
class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(regex=r'^[a-zA-Z]+([._-]?[a-zA-Z0-9]+)+$', min_length=3, required=True)
    password = serializers.CharField(write_only=True, required=True)
    password_confirmation = serializers.CharField(write_only=True, required=True)
    image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = User
        fields=("username", "first_name", "last_name", "email", "password", "password_confirmation", "image")
    
    def create(self, validated_data):
        username = validated_data.get('username')
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        email = validated_data.get('email')
        password = validated_data.get('password')
        password_confirmation = validated_data.get('password_confirmation')
        image = validated_data.get('image')

        if username and User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "Username must be unique."})

        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email addresses must be unique."})

        if password != password_confirmation:
            raise serializers.ValidationError({"password": "The password confirmation is not valid."})
        
        user = User(first_name=first_name, last_name=last_name, email=email, username=username, image=image)

        user.set_password(password)

        user.save()

        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True, required=False)
    private =  serializers.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['private', 'image']

    def update(self, instance, validated_data):
        instance.private = validated_data.get("private", instance.private)
        instance.image = validated_data.get("image", instance.image)
        instance.save()
        return instance

class LoginSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(regex=r'^[a-zA-Z]+([._-]?[a-zA-Z0-9]+)+$', min_length=3, max_length=30)
    password = serializers.CharField(min_length=8, max_length=50, write_only=True)

    class Meta:
        model=User
        fields = ('username', 'password')

    def create(self, validated_data):
        username = validated_data.get('username')
        password = validated_data.get('password')

        user = authentication.authenticate(username=username, password=password)

        if user == None:
            raise serializers.ValidationError({"username": "Username or password is incorrect"}, 404)
        
        return user