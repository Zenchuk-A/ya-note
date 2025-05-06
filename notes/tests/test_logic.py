# notes/tests/test_logic.py
import unittest
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    """A class to test whether a note can be created."""

    NOTE_TITLE = 'Заголовок заметки'
    NOTE_TEXT = 'Текст заметки'

    @classmethod
    def setUpTestData(cls):
        """Initialise the variables for the tests."""
        cls.author = User.objects.create(username='Юный натуралист')
        cls.url_add = reverse('notes:add')
        cls.url_done = reverse('notes:success')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {'title': cls.NOTE_TITLE, 'text': cls.NOTE_TEXT}

    def test_user_can_create_notes(self):
        """Check if the test user can create a note."""
        response = self.auth_client.post(self.url_add, data=self.form_data)
        self.assertRedirects(response, self.url_done)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Check if the anonymous user can create a note."""
        self.client.post(self.url_add, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)


class TestNoteEditDelete(TestCase):
    """A class to test editing/deleting notes."""

    NOTE_TITLE = 'Заголовок заметки'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'address_slug'
    NOTE_NEW_TITLE = 'Обновлённый заголовок заметки'
    NOTE_NEW_TEXT = 'Обновлённый текст заметки'
    NOTE_NEW_SLUG = 'address_new_slug'

    @classmethod
    def setUpTestData(cls):
        """Initialise the variables for the tests."""
        cls.author = User.objects.create(username='Юный натуралист')
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug=cls.NOTE_SLUG,
        )
        cls.note2 = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,
        )
        cls.url_add = reverse('notes:add')
        cls.url_done = reverse('notes:success')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.NOTE_NEW_TITLE,
            'text': cls.NOTE_NEW_TEXT,
            'slug': cls.NOTE_NEW_SLUG
        }

    def test_author_can_delete_note(self):
        """Check if the author can delete a note."""
        response = self.auth_client.delete(self.delete_url)
        self.assertRedirects(response, self.url_done)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_cant_delete_note_of_another_user(self):
        """Check if a user can delete another user's note."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)

    def test_author_can_edit_note(self):
        """Check if the author can edit a note."""
        response = self.auth_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.url_done)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_NEW_TITLE)
        self.assertEqual(self.note.text, self.NOTE_NEW_TEXT)
        self.assertEqual(self.note.slug, self.NOTE_NEW_SLUG)

    def test_user_cant_edit_note_of_another_user(self):
        """Check if a user can edit another user's note."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)

    def test_unique_slug(self):
        """Test the creation of a note with a duplicate title."""
        Note.objects.create(
            title='Первая заметка',
            text='Текст первой заметки.',
            author=self.author
        )
        with self.assertRaises(Exception):
            Note.objects.create(
                title='Первая заметка',
                text='Текст второй заметки.',
                author=self.author
            )

    def test_slug_from_title(self):
        """Test the creation of the correct slug from the title."""
        self.assertEqual(self.note2.slug, slugify(self.note2.title))
