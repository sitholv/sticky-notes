"""Optional administration of notes through Django's built-in admin."""

from django.contrib import admin

from .models import Note

admin.site.register(Note)
