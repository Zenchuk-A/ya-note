# notes/tests/test_routes.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """A class for testing routes."""

    @classmethod
    def setUpTestData(cls):
        """Initialise the variables for the tests."""
        cls.author = User.objects.create(username='Лёва Толстый')
        cls.reader = User.objects.create(username='Чтец обыкновенный')

        cls.note = Note.objects.create(
            title='Заголовок заметки',
            text='Тестовый текст',
            author=cls.author,
            slug='address_slug',
        )

    def test_pages_availability(self):
        """Test if pages are accessible to an anonymous user."""
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_detail_edit_delete(self):
        """Test that the author can work with notes, but other users cannot."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in (
                'notes:edit',
                'notes:detail',
                'notes:delete',
            ):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client_list_add(self):
        """Test redirects for an anonymous user for pages without params."""
        login_url = reverse('users:login')
        for name in ('notes:list', 'notes:add', 'notes:success'):
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_redirect_for_anonymous_client_detail_edit_delete(self):
        """Test redirects for an anonymous user for pages with params."""
        login_url = reverse('users:login')
        for name in (
            'notes:edit',
            'notes:detail',
            'notes:delete',
        ):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
