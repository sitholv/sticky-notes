"""The shared create/update form validates and strips whitespace."""

from django import forms

from .models import Note


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["title", "content"]
        help_texts = {
            "title": "Give your note a name. Maximum 120 characters.",
            "content": "Maximum 10,000 characters. Both fields are required.",
        }
        widgets = {
            "title": forms.TextInput(attrs={"autofocus": True}),
            "content": forms.Textarea(attrs={"rows": 10, "maxlength": 10000}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["aria-describedby"] = (
                f"id_{name}_help id_{name}_errors"
            )
