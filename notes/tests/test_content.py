# notes/tests/test_content.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNote(TestCase):
    """A class to test the content."""

    TITLE = 'Заголовок заметки'
    TEXT = 'Тестовый текст'
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        """Set initial settings for testing."""
        cls.author = User.objects.create(username='Лев Толстой')
        cls.creator = User.objects.create(username='Саня Пушкарь')

        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            author=cls.author,
            slug='address_slug',
        )

    def test_successful_creation(self):
        """Test the success of creation."""
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_title(self):
        """Test the creation of the correct title."""
        self.assertEqual(self.note.title, self.TITLE)

    def test_note_in_context(self):
        """Test that the created note is in the object_list context."""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_other_user_list(self):
        """Test that the user only gets their own notes."""
        self.client.force_login(self.creator)
        response = self.client.get(self.LIST_URL)
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_add_page_has_form(self):
        """Test if add page has note form."""
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:add'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_page_has_form(self):
        """Test if edit page has note form."""
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
