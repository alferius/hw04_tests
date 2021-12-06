from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class usersURLTest(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_access_for_all(self):
        """Доступ неавторизированного пользователя к страницам users"""
        pages_4_all = ('/auth/logout/', '/auth/signup/', '/auth/login/',
                       '/auth/password_reset/', '/auth/reset/done/')
        for page in pages_4_all:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'недоступна страница {page}')

        response = self.guest_client.get('/auth/password_change/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/auth/password_change/'
        )

        response = self.guest_client.get('/auth/password_change/done/',
                                         follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/auth/password_change/done/'
        )

    def test_access_for_autorized(self):
        """Доступ авторизированного пользователя к страницам users"""
        response = self.authorized_client.get('/auth/password_change/')
        self.assertEqual(response.status_code,
                         HTTPStatus.OK,
                         'страница password_change недоступна '
                         + 'авторизированному пользователю')
        self.assertTemplateUsed(response, 'users/password_change_form.html')

        response = self.authorized_client.get('/auth/password_change/done/')
        self.assertEqual(response.status_code,
                         HTTPStatus.OK,
                         'страница уведомления об изменении пароля недоступна '
                         + 'автору')
        self.assertTemplateUsed(response, 'users/password_change_done.html')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        link_URLs_n_templates = {
            'users:logout': 'users/logged_out.html',
            'users:signup': 'users/signup.html',
            'users:login': 'users/login.html',
            'users:password_reset': 'users/password_reset_form.html',
            'users:password_reset_done': 'users/password_reset_done.html',
            'users:password_reset_complete':
                                    'users/password_reset_complete.html',
        }
        for adress, template in link_URLs_n_templates.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(reverse(adress))
                self.assertTemplateUsed(response, template)
