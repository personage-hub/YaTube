from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post

URL_HOMEPAGE = reverse('index')
URL_NEW_POST = reverse('new_post')

User = get_user_model()

test_user = {
    'username': 'test_user',
    'email': 'test@ttesst.ru',
    'password': 'Test2password'
}


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(**test_user)
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.user = CacheTests.user
        self.authorized_client.force_login(self.user)

    def test_cache_index_page(self):
        """Проверка кэширования главной страницы."""
        form_data = {
            'text': 'TEST_TEST_TEST',
        }
        self.authorized_client.post(
            URL_NEW_POST,
            data=form_data,
            follow=True
        )
        Post.objects.filter(text=form_data['text']).delete()
        response = self.authorized_client.get(URL_HOMEPAGE)
        self.assertFalse(Post.objects.filter(text=form_data['text']).exists())
        self.assertContains(response, form_data['text'])
