from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Comment, Follow, Group, Post

User = get_user_model()
test_user = {
    'username': 'test_user1',
    'email': 'test@ttesst.ru',
    'password': 'Test2password'
}

test_user_2 = {
    'username': 'test_user2',
    'email': 'test@ttesst.ru',
    'password': 'Test2password'
}

test_group = {
    'title': 'Тестовая группа' * 5,
    'slug': 'test_slug1'
}

POST_TEXT = 'Тестовый пост с длинным текстом'
COMMENT_TEXT = 'Тестовый комментарий'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(**test_user)
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user
        )
        cls.group = Group.objects.create(**test_group)

    def test_str_method(self):
        """Вывод метода __str__ совпадает с ожидаемым."""
        post = PostModelTest.post
        expected = post.text[:15]
        self.assertEqual(str(post), expected)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(**test_group)

    def test_str_method(self):
        """Вывод метода __str__ совпадает с ожидаемым."""
        group = GroupModelTest.group
        expected = group.title
        self.assertEqual(str(group), expected)


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(**test_user)
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text=COMMENT_TEXT
        )

    def test_str_method(self):
        """Вывод str модели Comment соответвует ожиданию."""
        comment = CommentModelTest.comment
        expected = comment.text[:15]
        self.assertEqual(str(comment), expected)


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(**test_user)
        cls.author = User.objects.create(**test_user_2)
        cls.following = Follow.objects.create(user=cls.user, author=cls.author)

    def test_str_method(self):
        """Вывод str модели Follow соответствует ожиданию."""
        following = FollowModelTest.following
        expected = (
            f'Пользователь {following.user} подписан на {following.author}'
        )
        self.assertEqual(str(following), expected)
