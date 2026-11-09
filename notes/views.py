"""CRUD views with validation, POST redirects and confirmed deletion."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_safe

from .forms import NoteForm
from .models import Note


@require_safe
def note_list(request):
    return render(request, "notes/note_list.html", {
        "notes": Note.objects.all(),
    })


@require_safe
def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk)
    return render(request, "notes/note_detail.html", {"note": note})


@require_http_methods(["GET", "POST"])
def note_create(request):
    form = NoteForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        note = form.save()
        messages.success(request, "Note created.")
        return redirect(note)
    return render(request, "notes/note_form.html", {
        "form": form, "heading": "New note", "note": None,
    })


@require_http_methods(["GET", "POST"])
def note_update(request, pk):
    note = get_object_or_404(Note, pk=pk)
    form = NoteForm(
        request.POST if request.method == "POST" else None, instance=note
    )
    if request.method == "POST" and form.is_valid():
        note = form.save()
        messages.success(request, "Note updated.")
        return redirect(note)
    return render(request, "notes/note_form.html", {
        "form": form, "heading": "Edit note", "note": note,
    })


@require_http_methods(["GET", "POST"])
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == "POST":
        note.delete()
        messages.success(request, "Note deleted.")
        return redirect("notes:list")
    return render(request, "notes/note_confirm_delete.html", {"note": note})
