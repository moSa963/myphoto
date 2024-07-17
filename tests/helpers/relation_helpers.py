from relations.models import Follow

def create_follow(user, following):
    return Follow.objects.create(user=user, followed_user=following, verified=True)