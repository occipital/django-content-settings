from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        permissions = [
            ("can_read_todo", "Can view all books"),
            ("can_edit_todo", "Can view all books"),
        ]

    def __str__(self):
        return self.title
