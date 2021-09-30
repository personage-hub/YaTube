import shutil
import tempfile
import time

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

URL_HOMEPAGE = reverse('index')
URL_GROUP_PAGE = reverse('group_posts', kwargs={'slug': 'test_slug'})
URL_GROUP_PAGE_2 = reverse('group_posts', kwargs={'slug': 'test_slug_2'})
URL_NEW_POST = reverse('new_post')
URL_POST_EDIT = reverse(
    'edit_post',
    kwargs={'username': 'test_user', 'post_id': 1}
)
URL_PROFILE = reverse('profile', kwargs={'username': 'test_user'})
URL_POST = reverse('post', kwargs={'username': 'test_user', 'post_id': 1})

POST_TEXT = 'Тестовый №{index} с длинным текстом'
COMMENT_TEXT = 'Тестовый комментарий {index}'

PAGINATOR_TEST_LEN = 15
COMMENT_TEST_LEN = 10

test_group = {
    'title': 'Тестовая группа',
    'description': 'Группа созданная в тестах',
    'slug': 'test_slug'
}
test_group_2 = {
    'title': 'Тестовая группа 2',
    'description': 'Группа созданная в тестах 2',
    'slug': 'test_slug_2'
}

User = get_user_model()
test_user = {
    'username': 'test_user',
    'email': 'test@ttesst.ru',
    'password': 'Test2password'
}
small_gif = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00'
    b'\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
    b'\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
)
small_gif_1 = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00'
    b'\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
    b'\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
)

image = SimpleUploadedFile(
    name='small.gif',
    content=small_gif,
    content_type='image/gif'
)

image_1 = SimpleUploadedFile(
    name='small_1.gif',
    content=small_gif_1,
    content_type='image/gif'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(**test_user)
        cls.group = Group.objects.create(**test_group)
        cls.group_2 = Group.objects.create(**test_group_2)
        cls.post_1 = Post.objects.create(
            text='Тестовый №1 с длинным текстом',
            author=cls.user,
            image=image
        )
        time.sleep(0.1)  # Костыль для корректной работы с таймером Win
        cls.post_2 = Post.objects.create(
            text='Тестовый №2 с длинным текстом',
            author=cls.user,
            group=cls.group,
            image=image
        )
        comments = [
            Comment(
                post=PostPagesTests.post_1,
                author=PostPagesTests.user,
                text=COMMENT_TEXT.format(index=i),
            )
            for i in range(1, COMMENT_TEST_LEN)
        ]
        Comment.objects.bulk_create(comments)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = PostPagesTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': URL_HOMEPAGE,
            'posts/group.html': URL_GROUP_PAGE,
            'posts/edit_post.html': URL_NEW_POST
        }
        for template, url in templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_homepage_show_correct_context(self):
        """Шаблон homepage сформирован с нужным контекстом."""
        response = self.authorized_client.get(URL_HOMEPAGE)
        context = response.context['page'].object_list[1]
        page_context = {
            PostPagesTests.post_1.text: context.text,
            PostPagesTests.post_1.author: context.author,
            PostPagesTests.post_1.pub_date: context.pub_date,
            PostPagesTests.post_1.image: context.image,
            PostPagesTests.post_1.comments: context.comments,
        }
        for page_data, context_data in page_context.items():
            with self.subTest(post_data=page_data):
                self.assertEqual(context_data, page_data)

    def test_profile_page_correct_context(self):
        """Шаблон profile сформирован с нужным контекстом."""
        response = self.authorized_client.get(URL_PROFILE)
        context = response.context['page'].object_list[0]
        page_context = {
            PostPagesTests.post_2.text: context.text,
            PostPagesTests.post_2.author: context.author,
            PostPagesTests.post_2.pub_date: context.pub_date,
            PostPagesTests.post_2.image: context.image,
        }
        for page_data, context_data in page_context.items():
            with self.subTest(post_data=page_data):
                self.assertEqual(context_data, page_data)

    def test_post_page_correct_context(self):
        """Шаблон post сформирован с нужным контекстом."""
        response = self.authorized_client.get(URL_POST)
        context = response.context['post']
        page_context = {
            PostPagesTests.post_1.text: context.text,
            PostPagesTests.post_1.author: context.author,
            PostPagesTests.post_1.pub_date: context.pub_date,
            PostPagesTests.post_1.image: context.image,
        }
        for page_data, context_data in page_context.items():
            with self.subTest(post_data=page_data):
                self.assertEqual(context_data, page_data)

    def test_group_page_show_correct_context(self):
        """Шаблон group_page сформирован с нужным контекстом."""
        response = self.authorized_client.get(URL_GROUP_PAGE)
        context_post = response.context['page'].object_list[0]
        context_group = response.context['group']
        page_context = {
            PostPagesTests.post_2.text: context_post.text,
            PostPagesTests.post_2.author: context_post.author,
            PostPagesTests.post_2.group: context_group,
            PostPagesTests.post_2.pub_date: context_post.pub_date,
            PostPagesTests.post_2.image: context_post.image,
            PostPagesTests.group.title: context_group.title,
            PostPagesTests.group.description: context_group.description,
            PostPagesTests.group.slug: context_group.slug,
        }
        for page_data, context_data in page_context.items():
            with self.subTest(post_data=page_data):
                self.assertEqual(context_data, page_data)

    def test_new_post_page_get_correct_context(self):
        """
        Шаблон редактирования/создания поста
        сформированы с нужным контекстом.
        """
        urls = [URL_NEW_POST, URL_POST_EDIT]
        for url in urls:
            response = self.authorized_client.get(url)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
            }
            for value, context_form_field in form_fields.items():
                with self.subTest(value=value, url=url):
                    post_field = response.context['form'].fields[value]
                    self.assertIsInstance(post_field, context_form_field)

    def test_new_group_post_shows_on_homepage_and_group_page(self):
        """Пост отображается на главной стронице и на странице группы."""
        urls = [URL_HOMEPAGE, URL_GROUP_PAGE]
        for url in urls:
            with self.subTest(url=url):
                cache.clear()
                response = self.authorized_client.get(url)
                self.assertContains(response, PostPagesTests.post_2)

    def test_new_group_post_dont_shows_on_wrong_group_page(self):
        """Пост в группу не отображается на странице другой группы."""
        response = self.authorized_client.get(URL_GROUP_PAGE_2)
        self.assertNotContains(response, PostPagesTests.post_2)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(**test_user)
        cls.group = Group.objects.create(**test_group)
        cls.posts = []
        texts = [
            POST_TEXT.format(index=index + 1)
            for index in range(PAGINATOR_TEST_LEN)
        ]
        objects = [
            Post(
                text=text,
                author=cls.user
            )
            for text in texts
        ]
        Post.objects.bulk_create(objects)

    def setUp(self):
        self.guest_client = Client()
        self.user = PaginatorViewsTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_page_get_correct_number_of_posts_and_pages(self):
        """Проверка корректной работы паджинатора."""
        response = self.authorized_client.get(URL_HOMEPAGE)
        result = response.context['page']
        page_number = result.paginator.num_pages
        expected_pages = (
            (PAGINATOR_TEST_LEN // settings.ITEMS_ON_PAGE) + 1
            if PAGINATOR_TEST_LEN % settings.ITEMS_ON_PAGE != 0
            else PAGINATOR_TEST_LEN / settings.ITEMS_ON_PAGE
        )
        item_number = len(result.object_list)
        expected_item = settings.ITEMS_ON_PAGE
        self.assertEqual(page_number, expected_pages)
        self.assertEqual(item_number, expected_item)
