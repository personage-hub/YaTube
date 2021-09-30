import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
IMAGE_NAME = 'small.gif'
URL_HOMEPAGE = reverse('index')
URL_NEW_POST = reverse('new_post')
URL_POST_EDIT = reverse(
    'edit_post',
    kwargs={'username': 'test_user', 'post_id': 1}
)
URL_POST = reverse(
    'post',
    kwargs={'username': 'test_user', 'post_id': 1}
)
URL_IMAGE = f'posts/{IMAGE_NAME}'

small_gif = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00'
    b'\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
    b'\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
)
image = SimpleUploadedFile(
    name=IMAGE_NAME,
    content=small_gif,
    content_type='image/gif'
)

User = get_user_model()

test_user = {
    'username': 'test_user',
    'email': 'test@ttesst.ru',
    'password': 'Test2password'
}


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(**test_user)
        Post.objects.create(
            text='Тестовый №1 с длинным текстом',
            author=cls.user
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.user = PostFormTests.user
        self.authorized_client.force_login(self.user)

    def test_new_post(self):
        """Проверка формы создания поста."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый №2 с длинным постом',
            'image': image
        }
        response = self.authorized_client.post(
            URL_NEW_POST,
            data=form_data,
            follow=True
        )
        last_post = Post.objects.first()
        self.assertRedirects(response, URL_HOMEPAGE)
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.author, PostFormTests.user)
        self.assertEqual(last_post.image.name, URL_IMAGE)
        self.assertEqual(last_post.group, form_data.get('slug'))

    def test_post_edit(self):
        """Проверка формы редактирования поста."""
        post_count = Post.objects.count()
        original_post = Post.objects.get(pk=1)
        original_text = original_post.text
        form_data = {
            'text': 'Отредактированный пост №1',
            'slug': '',
        }
        response = self.authorized_client.post(
            URL_POST_EDIT,
            data=form_data,
            follow=True
        )
        edit_post = Post.objects.get(pk=1)
        self.assertRedirects(response, URL_POST)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertNotEqual(edit_post.text, original_text)
        self.assertEqual(edit_post.author, original_post.author)
        self.assertEqual(edit_post.group, original_post.group)
