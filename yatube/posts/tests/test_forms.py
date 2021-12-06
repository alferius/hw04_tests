from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.user = User.objects.create_user(username='auth')
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Для тестов',
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тест, тест, тест',
            group=self.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        test_dic = {
            'text': 'Ещё один тест',
            'group_id': self.group.id,
            'author_id': self.user.id
        }
        response = self.authorized_client.post(
            reverse('post:post_create'),
            data=test_dic,
            follow=True
        )
        self.assertRedirects(response, reverse('post:profile',
                             kwargs={'username': 'auth'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        response = self.authorized_client.get(reverse('post:post_edit',
                                              kwargs={'post_id': 1}))
        old_post_text = response.context.get('form').initial['text']
        test_dic = {
            'text': 'Ещё один тест',
            'group_id': self.group.id,
            'author_id': self.user.id
        }
        response = self.authorized_client.post(
            reverse('post:post_edit', kwargs={'post_id': 1}),
            data=test_dic,
            follow=True
        )
        response = self.authorized_client.get(reverse('post:post_edit',
                                              kwargs={'post_id': 1}))
        new_post_text = response.context.get('form').initial['text']
        self.assertNotEqual(old_post_text, new_post_text)
