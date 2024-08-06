from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.db.models import Count

from blog.models import Category, Post, Comment
from .constants import PAGINATION
from .models import User
from .forms import PostForm, CommentForm


class PostDispatchMixin:

    def dispatch(self, request, *args, **kwargs):
        post = super().get_object()
        if post.author != self.request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class CommentDispatchMixin:

    def dispatch(self, request, *args, **kwargs):
        comment = super().get_object()
        user = self.request.user
        if user != comment.author:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class IndexListView(ListView):
    """Выводит главную страницу сайта."""

    model = Post
    paginate_by = PAGINATION
    template_name = 'blog/index.html'

    def get_queryset(self):
        return (Post.objects.annotate(comment_count=Count('comments')).filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True).order_by('-pub_date')).select_related(
                'author', 'location', 'category')


class UserListView(ListView):
    model = Post
    paginate_by = PAGINATION
    ordering = '-pub_date'
    template_name = 'blog/profile.html'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        if self.request.user == user:
            return (Post.objects.annotate(
                comment_count=Count('comments')).filter(
                author=user).order_by('-pub_date'))
        return (Post.objects.annotate(comment_count=Count('comments')).filter(
            author=user,
            is_published=True,
            pub_date__lte=timezone.now()).order_by('-pub_date'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs['username'])
        context['profile'] = user
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ('username', 'last_name', 'first_name', 'email',)
    template_name = 'blog/user.html'

    def get_object(self):
        user = get_object_or_404(User, username=self.request.user)
        return user

    def get_success_url(self, **kwargs):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user})


class PostDetailView(DetailView):
    model = Post
    pk_field = 'post_id'
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_object(self):
        post = super().get_object()
        user = self.request.user
        if post.is_published is False and user != post.author:
            raise Http404
        return super().get_object()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.filter(
            post=self.kwargs['post_id']).select_related('post')
        return context


class PostUpdateView(LoginRequiredMixin, PostDispatchMixin, UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    pk_field = 'post_id'
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class PostDeleteView(LoginRequiredMixin, PostDispatchMixin, DeleteView):
    model = Post
    from_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    pk_field = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = super().get_object()
        form = PostForm(instance=instance)
        context['form'] = form
        return context

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user})


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    ordering = '-pub_date'
    paginate_by = PAGINATION

    def get_queryset(self):
        return (Post.objects.filter(
            category__slug=self.kwargs['category_slug'],
            is_published=True,
            pub_date__lte=timezone.now()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True)
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    post_object = None
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class CommentDeleteView(LoginRequiredMixin, CommentDispatchMixin, DeleteView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
    pk_field = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class CommentUpdateView(LoginRequiredMixin, CommentDispatchMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
    pk_field = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})
