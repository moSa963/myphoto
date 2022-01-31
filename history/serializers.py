from rest_framework import serializers

class CommentHistorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    post_id = serializers.IntegerField(read_only=True)
    post_title = serializers.CharField(read_only=True)

    reply_to_id = serializers.IntegerField(read_only=False)
    reply_to_username = serializers.CharField(read_only=False)
    reply_to_text = serializers.CharField(read_only=False)
    reply_to_date = serializers.CharField(read_only=False)

    text = serializers.CharField(max_length=1000)
    edited = serializers.BooleanField(default=False)
    date = serializers.DateTimeField(read_only=True)
    user_liked = serializers.IntegerField(read_only=True)
    likes = serializers.IntegerField(source="like", read_only=True)