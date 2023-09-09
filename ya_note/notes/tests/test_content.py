from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestListNote(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )

    def test_notes_list_for_different_users(self):
        user_statuses = [
            (self.author, True),
            (self.reader, False)
        ]
        client = Client()
        for user, status in user_statuses:
            with self.subTest(user=user):
                client.force_login(user)
                response = client.get(reverse('notes:list'))
                content = response.context['object_list']
                self.assertTrue((self.note in content) is status)

    def test_pages_contains_form(self):
        urls = [
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        ]
        client = Client()
        for name, args in urls:
            with self.subTest(name=name):
                client.force_login(self.author)
                url = reverse(name, args=args)
                response = client.get(url)
                self.assertIn('form', response.context)
