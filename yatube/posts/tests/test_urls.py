from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        # автор тестовой записи
        self.user = User.objects.create_user(username='auth')
        # просто зарегистрированный пользователь
        self.second_user = User.objects.create_user(username='leo')
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Для тестов',
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тест, тест, тест',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_second_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_second_client.force_login(self.second_user)

    def test_access_for_all(self):
        """Доступ неавторизированного пользователя к страницам"""
        pages_4_all = ('/', '/group/testslug/', '/profile/auth/',
                       '/posts/1/',)
        for page in pages_4_all:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'недоступна страница {page}')

        response = self.guest_client.get('/unknown/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND,
                         'внезапно стала доступна страница unknown')

        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

        response = self.guest_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/posts/1/edit/'
        )

    def test_access_for_autorized(self):
        """Доступ авторизированного пользователя к страницам"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code,
                         HTTPStatus.OK,
                         'страница create недоступна '
                         + 'авторизированному пользователю')

        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code,
                         HTTPStatus.OK,
                         'страница редактирования недоступна автору')

        response = self.authorized_second_client.get('/posts/1/edit/',
                                                     follow=True)
        self.assertRedirects(response, '/posts/1/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        link_URLs_n_templates = {
            '/': 'posts/index.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/group/testslug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
        }
        for adress, template in link_URLs_n_templates.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
