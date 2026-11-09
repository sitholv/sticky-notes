"""Persist a note's title, content and creation/update times."""

from django.core.validators import MaxLengthValidator
from django.db import models
from django.urls import reverse


class Note(models.Model):
    title = models.CharField(max_length=120)
    content = models.TextField(validators=[MaxLengthValidator(10000)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-pk"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("notes:detail", args=[self.pk])
