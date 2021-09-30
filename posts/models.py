from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F, ForeignKey, Q

User = get_user_model()


class Group(models.Model):
    """
    Модель для объекта Group.
    """
    title = models.CharField('Group name', max_length=200)
    slug = models.SlugField('Group slug', unique=True)
    description = models.TextField('Group description')

    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    def __str__(self):
        return self.title


class Post(models.Model):
    """
    Модель для объекта Post.
    """
    text = models.TextField('Posts text')
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts'
    )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    """Модель для объекта Комментарий."""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField('Comment text')
    created = models.DateTimeField('date created', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-created',)

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    """Модель для отслеживания подписок пользователей."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_together'
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='self_following'
            ),
        ]

    def __str__(self):
        return f'Пользователь {self.user} подписан на {self.author}'
