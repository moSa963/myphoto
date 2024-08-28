from django.contrib.auth import get_user_model
from django.db.models import Count, OuterRef, Q, Subquery
from django.contrib.auth.models import UserManager

class UserManager(UserManager):
    def for_user(self, user, key: str=""):
        following_status_subquery = get_user_model().objects.filter(
            followers__user_id=user.id,
            pk=OuterRef('pk')
        ).values('followers__verified')[:1]

        query = get_user_model().objects.filter(
            username__icontains=key
        ).annotate(
            followers_count=Count("followers", filter=Q(followers__verified=True)), 
            following_status=Subquery(following_status_subquery)
        ).order_by("-followers_count")
        
        return query
    
    
    
    