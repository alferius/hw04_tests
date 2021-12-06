from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.user = User.objects.create_user(username='auth')
        self.second_user = User.objects.create_user(username='leo')
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
        self.second_authorized_client = Client()
        self.second_authorized_client.force_login(self.second_user)

    def test_names_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        link_names_n_templates = {
            reverse('post:index'): 'posts/index.html',
            reverse('post:group_list',
                    kwargs={'SlugField': 'testslug'}): 'posts/group_list.html',
            reverse('post:profile',
                    kwargs={'username': 'auth'}): 'posts/profile.html',
            reverse('post:post_detail',
                    kwargs={'post_id': '1'}): 'posts/post_detail.html',
            reverse('post:post_edit',
                    kwargs={'post_id': '1'}): 'posts/create_post.html',
            reverse('post:post_create'): 'posts/create_post.html',
        }
        for adress, template in link_names_n_templates.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_paginator_n_context_4_pages_with_posts_list(self):
        """проверяем пагинатор и содержимое на страницах со списком статей"""
        link_names = (
            reverse('post:index'),
            reverse('post:group_list',
                    kwargs={'SlugField': 'testslug'}),
            reverse('post:profile',
                    kwargs={'username': 'auth'}),
        )
        test_dic = {
            'text': 'Тест, тест, тест',
            'group.title': 'Тестовая группа',
            'group.slug': 'testslug',
            'author.username': 'auth',
        }
        for name in link_names:
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                first_post = response.context.get('page_obj')[0]
                post_group = response.context.get('group')
                post_author = response.context.get('username')

                self.assertEqual(len(
                    response.context['page_obj']), 10, 'неверное количество '
                    + f'постов на первой странице {name}')
                response = self.authorized_client.get(name + '?page=2')
                self.assertEqual(len(
                    response.context['page_obj']), 5, 'неверное количество '
                    + f'постов на второй странице {name}')

                self.assertEqual(test_dic['text'],
                                 first_post.text,
                                 f'текст статьи на {name} не соответствует '
                                 + 'передаваемому')
                self.assertEqual(test_dic['group.title'],
                                 first_post.group.title,
                                 f'группа статьи на {name} не соответствует '
                                 + 'передаваемой')
                self.assertEqual(test_dic['author.username'],
                                 first_post.author.username,
                                 f'автор статьи на {name} не соответствует '
                                 + 'передаваемому')

                if name == '/group/testslug/':
                    self.assertEqual(test_dic['group.slug'],
                                     post_group.slug,
                                     f'ошибка фильтра по группе на {name}')

                if name == '/group/auth/':
                    self.assertEqual(test_dic['author.username'],
                                     post_author.username,
                                     f'ошибка фильтра по автору на {name}')

    def test_post_detail_show_correct_context(self):
        """проверяем post_detail на соответствие id, правильности context"""
        response = self.authorized_client.get(reverse('post:post_detail',
                                              kwargs={'post_id': '1'}))
        guest_response = self.guest_client.get(reverse('post:post_detail',
                                               kwargs={'post_id': '1'}))
        second_authorized_response = self.second_authorized_client.get(
            reverse('post:post_detail',
                    kwargs={'post_id': '1'}))

        self.assertEqual(
            response.context['post'].id, 1, 'вызван не тот пост')

        self.assertEqual(
            response.context['post'].text,
            'Тест, тест, тест', 'передаётся не тот текст статьи')

        self.assertEqual(
            response.context['title'],
            response.context['post'].text[:30],
            'передаётся не правильный заголовок')

        self.assertEqual(
            response.context['posts_count'],
            15, 'передаётся не правильное количество статей')

        self.assertFalse(
            guest_response.context['is_edit'],
            'передаётся не правильный флаг редактирования')

        self.assertFalse(
            second_authorized_response.context['is_edit'],
            'передаётся не правильный флаг редактирования')

    def test_post_edit_show_correct_context(self):
        """проверяем post_edit на id, правильность context и формы"""
        response = self.authorized_client.get(reverse('post:post_edit',
                                              kwargs={'post_id': '1'}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        form_values = {
            'text': 'Тест, тест, тест',
            'group': 1,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                text_field = response.context.get('form').initial[value]
                self.assertIsInstance(form_field, expected, f'поле {value} '
                                      + 'не того типа')

                self.assertEqual(text_field, form_values[value],
                                 'передаётся не тот текст формы')

                self.assertTrue(response.context['is_edit'],
                                'передаётся не правильный флаг редактирования')

    def test_post_create_show_correct_context(self):
        """проверяем post_create на правильность формы"""
        response = self.authorized_client.get(reverse('post:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected, f'поле {value} '
                                      + 'не того типа')
        self.assertFalse(response.context['is_edit'],
                         'передаётся не правильный флаг редактирования')

    def test_new_record_add_2_index_group_n_profile(self):
        """Тестирование отображения новой записи"""
        self.new_group = Group.objects.create(
            title='Новая группа',
            slug='newslug',
            description='Ещё тест',
        )

        self.new_post = Post.objects.create(
            author=self.second_user,
            text='Тестирование отображения новой записи',
            group=self.new_group,
        )

        link_names = (
            reverse('post:index'),
            reverse('post:group_list',
                    kwargs={'SlugField': 'newslug'}),
            reverse('post:profile',
                    kwargs={'username': 'leo'}),
        )
        test_dic = {
            'text': 'Тестирование отображения новой записи',
            'group.title': 'Новая группа',
            'group.slug': 'newslug',
            'author.username': 'leo',
        }
        for name in link_names:
            with self.subTest(name=name):
                response = self.second_authorized_client.get(name)
                first_post = response.context.get('page_obj')[0]
                post_group = response.context.get('group')
                post_author = response.context.get('username')

                self.assertEqual(test_dic['text'],
                                 first_post.text,
                                 f'текст статьи на {name} не соответствует '
                                 + 'передаваемому')
                self.assertEqual(test_dic['group.title'],
                                 first_post.group.title,
                                 f'группа статьи на {name} не соответствует '
                                 + 'передаваемой')
                self.assertEqual(test_dic['author.username'],
                                 first_post.author.username,
                                 f'автор статьи на {name} не соответствует '
                                 + 'передаваемому')

                if name == '/group/testslug/':
                    self.assertEqual(test_dic['group.slug'],
                                     post_group.slug,
                                     f'ошибка фильтра по группе на {name}')

                if name == '/group/auth/':
                    self.assertEqual(test_dic['author.username'],
                                     post_author.username,
                                     f'ошибка фильтра по автору на {name}')
