import random
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Comment, Group, Post

URL_HOMEPAGE = '/'
URL_GROUP_PAGE = '/group/test_slug/'
URL_NEW_POST = '/new/'
URL_USER_PROFILE = '/test_user/'
URL_POST = '/test_user/1/'
URL_POST_EDIT = '/test_user/1/edit/'
URL_LOGIN = '/auth/login/?next='
URL_NON_EXIST = 'url_non_exist' + str(random.randint(0, 10000))

User = get_user_model()

COMMENT_TEXT = 'Тестовый комментарий {index}'

COMMENT_TEST_LEN = 10

test_user_author = {
    'username': 'test_user',
    'email': 'test@ttesst.ru',
    'password': 'Test2password'
}
test_user_not_author = {
    'username': 'random_user',
    'email': 'test2@ttesst.ru',
    'password': 'Test2password'
}
test_group = {
    'title': 'Тестовая группа ' * 5,
    'slug': 'test_slug'
}


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get(URL_HOMEPAGE)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class URLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(**test_user_author)
        cls.post_1 = Post.objects.create(
            text='Тестовый №1 с длинным текстом',
            author=cls.author
        )
        cls.non_author = User.objects.create_user(**test_user_not_author)
        cls.group = Group.objects.create(**test_group)
        comments = [
            Comment(
                post=URLTest.post_1,
                author=URLTest.author,
                text=COMMENT_TEXT.format(index=i),
            )
            for i in range(1, COMMENT_TEST_LEN)
        ]
        Comment.objects.bulk_create(comments)

    def setUp(self):
        self.guest_client = Client()
        self.author = URLTest.author
        self.non_author = URLTest.non_author
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)
        self.authorized_client_non_author = Client()
        self.authorized_client_non_author.force_login(self.non_author)

    def test_url_url_exists_at_desired_location_authorized(self):
        """Страницы доступны для просмотра авторизиованным пользователем."""
        urls = [
            URL_HOMEPAGE,
            URL_GROUP_PAGE,
            URL_NEW_POST,
            URL_USER_PROFILE,
            URL_POST,
            URL_POST_EDIT
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client_author.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_url_exists_at_desired_location_anon(self):
        """Страницы доступны для просмотра неавторизованным пользователем."""
        urls = [
            URL_HOMEPAGE,
            URL_GROUP_PAGE,
            URL_USER_PROFILE,
            URL_POST
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_new_edit_post_redirects_anon_on_login(self):
        """
        Страница создания и редактирования поста
        перенаправит анонимного пользователя
        на страницу логина.
        """
        redirect_pages = {
            URL_NEW_POST: (URL_LOGIN + URL_NEW_POST),
            URL_POST_EDIT: (URL_LOGIN + URL_POST_EDIT)
        }
        for url, redirect_page in redirect_pages.items():
            with self.subTest(redirect_page=redirect_page):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect_page)

    def test_edit_post_redirect_non_author_on_post_page_edit(self):
        """
        Страница редактирования поста перенаправит не автора просмотра
        на страницу просмотра поста.
        """
        response = self.authorized_client_non_author.get(
            URL_POST_EDIT, follow=True
        )
        self.assertRedirects(response, URL_POST)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            URL_HOMEPAGE: 'posts/index.html',
            URL_GROUP_PAGE: 'posts/group.html',
            URL_NEW_POST: 'posts/edit_post.html',
            URL_POST_EDIT: 'posts/edit_post.html',
            URL_NON_EXIST: 'misc/404.html',
            URL_POST: 'posts/includes/comments.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client_author.get(url)
                self.assertTemplateUsed(response, template)

    def test_page_not_found_get_404(self):
        """Если страница не найдена то возращается ошибка 404."""
        urls = [
            URL_NON_EXIST,
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
