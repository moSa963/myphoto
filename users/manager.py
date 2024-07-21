from django.contrib.auth import get_user_model
from django.db.models import Case, When, Count, F, BooleanField
from django.contrib.auth.models import UserManager

class UserManager(UserManager):
    def for_user(self, user, key: str=""):
        query = get_user_model().objects.filter(username__icontains=key).annotate(
            followers_count=Count("followers"), 
            following_status=Case(When(followers__user_id=user.id, then=F("followers__verified")), output_field=BooleanField(null=True))
        ).order_by("followers_count")
        
        return query