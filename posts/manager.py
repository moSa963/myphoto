from django.db import models


class PostManager(models.Manager):
    def delete(self) -> tuple[int, dict[str, int]]:
        return super().delete()

class PostImageManager(models.Manager):
    def delete(self) -> tuple[int, dict[str, int]]:
        return super().delete()