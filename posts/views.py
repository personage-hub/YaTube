from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

POST_NOT_FOUND = 'Запрошенного поста не существует'


def index(request):
    post_list = Post.objects.select_related('group').all()
    paginator = Paginator(post_list, settings.ITEMS_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    paginator = Paginator(posts_list, settings.ITEMS_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/group.html',
                  {'group': group, 'page': page})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    post_list = author.posts.all()
    paginator = Paginator(post_list, settings.ITEMS_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'user': user,
        'author': author,
        'page': page,
    }
    return render(request, 'posts/profile.html', context)


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author__username=username, id=post_id)
    user = request.user
    form = CommentForm(request.POST or None)
    context = {
        'user': user,
        'author': author,
        'post': post,
        'form': form,
    }
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('post', username=author.username, post_id=post.id)
    return render(request, 'posts/post.html', context)


@login_required
def new_post(request):
    context = {'edit_post': False}
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        context.update({'form': form})
        return render(request, 'posts/edit_post.html', context)
    context.update({'form': form})
    return render(request, 'posts/edit_post.html', context)


@login_required
def post_edit(request, username, post_id):
    context = {'edit_post': True}
    post = get_object_or_404(Post, pk=post_id)
    user_auth = request.user
    author = get_object_or_404(User, username=username)
    if user_auth != author:
        return redirect('post', username=author.username, post_id=post.id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('post', username=username, post_id=post_id)
    context.update({'form': form, 'post': post})
    return render(request, 'posts/edit_post.html', context)


@login_required
def add_comment(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author__username=username, id=post_id)
    user = request.user
    form = CommentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('post', username=username, post_id=post_id)
    context = {
        'user': user,
        'author': author,
        'post': post,
        'form': form,
    }
    return render(request, 'posts/post.html', context)


@login_required
def follow_index(request):
    username = request.user.username
    user = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author__following__user=user)
    paginator = Paginator(post_list, settings.ITEMS_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/follow.html', {'page': page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    username = request.user.username
    user = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=user, author=author).exists()
    if author != user and not is_follower:
        Follow.objects.create(user=user, author=author)
    return redirect('profile', username=author.username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    username = request.user.username
    user = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=user, author=author).exists()
    if is_follower:
        Follow.objects.get(user=user, author=author).delete()
    return redirect('profile', username=author.username)


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)
