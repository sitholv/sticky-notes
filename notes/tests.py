"""Regression tests for models, forms, routes and CRUD use cases."""

from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import resolve, reverse

from .forms import NoteForm
from .models import Note


class NoteModelTests(TestCase):
    def test_string_and_detail_url(self):
        note = Note.objects.create(title="Read", content="Django guide")
        self.assertEqual(str(note), "Read")
        self.assertEqual(note.get_absolute_url(), f"/notes/{note.pk}/")
        self.assertIsNotNone(note.created_at)
        self.assertIsNotNone(note.updated_at)

    def test_model_limits(self):
        for title, content in [("x" * 121, "Read"), ("Read", "x" * 10001)]:
            with self.assertRaises(ValidationError):
                Note(title=title, content=content).full_clean()

    def test_newest_edited_first(self):
        first = Note.objects.create(title="First", content="One")
        second = Note.objects.create(title="Second", content="Two")
        self.assertEqual(list(Note.objects.all()), [second, first])
        first.content = "Changed"
        first.save()
        self.assertEqual(Note.objects.first(), first)


class NoteFormTests(TestCase):
    def test_valid_input_is_stripped(self):
        form = NoteForm({"title": " Read ", "content": " Guide "})
        self.assertTrue(form.is_valid())
        note = form.save()
        self.assertEqual((note.title, note.content), ("Read", "Guide"))

    def test_required_fields(self):
        for data in [{}, {"title": " ", "content": "Read"},
                     {"title": "Read", "content": "\n "}]:
            self.assertFalse(NoteForm(data).is_valid())
        self.assertEqual(Note.objects.count(), 0)

    def test_boundaries(self):
        self.assertTrue(NoteForm({
            "title": "t" * 120, "content": "c" * 10000,
        }).is_valid())
        for data in [{"title": "t" * 121, "content": "Read"},
                     {"title": "Read", "content": "c" * 10001}]:
            self.assertFalse(NoteForm(data).is_valid())


class NoteViewTests(TestCase):
    def setUp(self):
        self.note = Note.objects.create(title="Soccer", content="Training")

    def url(self, name):
        return reverse(f"notes:{name}", args=[self.note.pk])

    def test_list_and_detail(self):
        response = self.client.get(reverse("notes:list"))
        self.assertContains(response, "Soccer")
        self.assertTemplateUsed(response, "notes/note_list.html")
        response = self.client.get(self.url("detail"))
        self.assertContains(response, "Training")
        self.assertTemplateUsed(response, "notes/base.html")

    def test_empty_state(self):
        Note.objects.all().delete()
        self.assertContains(self.client.get("/"), "No notes yet.")

    def test_create_get(self):
        response = self.client.get(reverse("notes:create"))
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, 'type="submit"')
        self.assertEqual(Note.objects.count(), 1)

    def test_create_post_and_redirect(self):
        response = self.client.post(reverse("notes:create"), {
            "title": "Technology", "content": "Read an article",
        })
        note = Note.objects.get(title="Technology")
        self.assertRedirects(response, note.get_absolute_url())

    def test_invalid_create_preserves_input(self):
        response = self.client.post(reverse("notes:create"), {
            "title": "", "content": "Keep my draft",
        })
        self.assertContains(response, "Keep my draft")
        self.assertContains(response, "This field is required.")
        self.assertEqual(Note.objects.count(), 1)

    def test_update_get_does_not_write(self):
        response = self.client.get(self.url("update"))
        self.assertContains(response, "Soccer")
        self.note.refresh_from_db()
        self.assertEqual(self.note.content, "Training")

    def test_update_preserves_identity(self):
        response = self.client.post(self.url("update"), {
            "title": "Match", "content": "Saturday",
        })
        self.assertRedirects(response, self.url("detail"))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Match")
        self.assertEqual(Note.objects.count(), 1)

    def test_invalid_update_leaves_database_unchanged(self):
        response = self.client.post(self.url("update"), {
            "title": "Changed", "content": " ",
        })
        self.assertEqual(response.status_code, 200)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Soccer")

    def test_delete_get_only_confirms(self):
        response = self.client.get(self.url("delete"))
        self.assertContains(response, "Keep note")
        self.assertContains(response, "cannot be undone")
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())

    def test_delete_post(self):
        response = self.client.post(self.url("delete"))
        self.assertRedirects(response, reverse("notes:list"))
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_unknown_note_is_404(self):
        for name in ["detail", "update", "delete"]:
            url = reverse(f"notes:{name}", args=[99999])
            self.assertEqual(self.client.get(url).status_code, 404)
            expected = 405 if name == "detail" else 404
            self.assertEqual(self.client.post(url, {}).status_code, expected)

    def test_unsupported_methods_are_rejected(self):
        for url in ["/", reverse("notes:create"), self.url("detail"),
                    self.url("update"), self.url("delete")]:
            self.assertEqual(self.client.put(url).status_code, 405)
        self.assertEqual(self.client.post("/").status_code, 405)

    def test_note_html_is_escaped(self):
        self.note.title = "<script>alert(1)</script>"
        self.note.content = '<img src=x onerror="alert(1)">'
        self.note.save()
        for url in ["/", self.url("detail")]:
            response = self.client.get(url)
            self.assertNotContains(response, "<script>alert(1)</script>")
            self.assertContains(response, "&lt;script&gt;")
            self.assertNotContains(response, "<img src=x")

    def test_csrf_is_enforced_for_all_writes(self):
        client = Client(enforce_csrf_checks=True)
        for url in [reverse("notes:create"), self.url("update"),
                    self.url("delete")]:
            response = client.post(url, {"title": "No", "content": "No"})
            self.assertEqual(response.status_code, 403)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Soccer")

    def test_csrf_valid_form_can_create(self):
        client = Client(enforce_csrf_checks=True)
        client.get(reverse("notes:create"))
        token = client.cookies["csrftoken"].value
        response = client.post(reverse("notes:create"), {
            "csrfmiddlewaretoken": token,
            "title": "Reading", "content": "Technology articles",
        })
        self.assertEqual(response.status_code, 302)

    def test_namespaced_routes(self):
        self.assertEqual(resolve("/").view_name, "notes:list")
        self.assertEqual(resolve("/notes/new/").view_name, "notes:create")
        for name in ["detail", "update", "delete"]:
            actual = resolve(self.url(name)).view_name
            self.assertEqual(actual, f"notes:{name}")
