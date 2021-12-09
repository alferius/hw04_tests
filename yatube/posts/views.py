from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from posts.forms import PostForm

from yatube.settings import POSTS_ON_THE_PAGES

from .models import Group, Post, User


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, POSTS_ON_THE_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, SlugField):
    group = get_object_or_404(Group, slug=SlugField)
    posts = group.groups4all.all()
    paginator = Paginator(posts, POSTS_ON_THE_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    paginator = Paginator(posts, POSTS_ON_THE_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'username': user,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    is_edit = False
    post = get_object_or_404(Post, id=post_id)
    user = get_object_or_404(User, username=post.author)
    if post.author == request.user:
        is_edit = True
    posts_count = user.posts.all().count()
    context = {
        'title': post.text[:30],
        'post': post,
        'posts_count': posts_count,
        'is_edit': is_edit
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    is_edit = False
    form = PostForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            cleaned_text = form.cleaned_data['text']
            cleaned_group = form.cleaned_data['group']
            user = request.user
            if cleaned_group is None:
                new_post = Post(
                    text=cleaned_text,
                    author_id=user.id,
                    pub_date=datetime.now()
                )
            else:
                group = get_object_or_404(Group, title=cleaned_group)
                group_id = group.id
                new_post = Post(
                    text=cleaned_text,
                    author_id=user.id,
                    group_id=group_id,
                    pub_date=datetime.now()
                )
            new_post.save()
            return redirect(reverse('post:profile', args=[user.username]))
        else:
            return render(request, 'posts/create_post.html',
                          {'form': form, 'is_edit': is_edit})

    form = {'form': form, 'is_edit': is_edit}
    return render(request, 'posts/create_post.html', form)


@login_required
def post_edit(request, post_id):
    post = Post.objects.get(pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    if post.author == request.user:
        is_edit = True
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                return redirect(reverse('post:post_detail', args=[post_id]))
            else:
                return render(request, 'posts/create_post.html',
                              {'form': form, 'is_edit': is_edit})
        form = {'form': form, 'is_edit': is_edit}
        return render(request, 'posts/create_post.html', form)
    else:
        return redirect(reverse('post:post_detail', args=[post_id]))
