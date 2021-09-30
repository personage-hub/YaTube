from django.contrib import admin

from .models import Comment, Follow, Group, Post

EMPTY_VALUE = '-пусто-'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = EMPTY_VALUE


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    empty_value_display = EMPTY_VALUE


@admin.register(Follow)
class FollowingAdmin(admin.ModelAdmin):
    list_display = ('author',)
    search_fields = ('author',)
    list_filter = ('user',)
    empty_value_display = EMPTY_VALUE


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'text')
    search_fields = ('text',)
    list_filter = ('author',)
    empty_value_display = EMPTY_VALUE
