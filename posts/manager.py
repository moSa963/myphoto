from django.db import models
from django.db.models import Q
from posts.models import User
from typing import Self

class PostManager(models.Manager):
    def related_posts(self, user: User, order_by: str="new") -> Self:
        q = self.select_related("user").filter(
            Q(user_id=user.id) |
                (Q(private=False) &
                    (Q(user__private=False) |
                        (Q(user__followers__user_id=user.id) & Q(user__followers__verified=True))
                    )
                )).prefetch_related('images')
        
        q = self._order(q, order_by)
        
        return q
    
    def _order(self, q, order_by):
        by = "-created_at"
        
        if order_by == "old":
            by = "created_at"
            
        return q.order_by(by)
    
class PostImageManager(models.Manager):
    def delete(self) -> tuple[int, dict[str, int]]:
        return super().delete()