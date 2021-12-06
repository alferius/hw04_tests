from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class UsersViewsTest(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.user = User.objects.create_user(username='auth')
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Для тестов',
        )
        for _ in range(15):
            self.post = Post.objects.create(
                author=self.user,
                text='Тест, тест, тест',
                group=self.group,
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_names_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        link_names_n_templates = {
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_reset'): 'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
            reverse('users:password_change'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
        }

        for adress, template in link_names_n_templates.items():
            with self.subTest(adress=adress):
                self.authorized_client.force_login(self.user)
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
