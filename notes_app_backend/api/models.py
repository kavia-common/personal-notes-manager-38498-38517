from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Note(models.Model):
    """
    A note belonging to a specific user.
    """
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]  # Default ordering for querysets

    def __str__(self) -> str:
        return f"{self.title} (owner={self.owner_id})"
