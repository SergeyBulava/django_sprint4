from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView)
from blog.models import Category, Post, Comment
from .models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from .forms import PostForm, CommentForm
from django.core.exceptions import PermissionDenied
from django.db.models import Count


class IndexListView(ListView):
    """Выводит главную страницу сайта."""

    model = Post
    paginate_by = 10
    template_name = 'blog/index.html'

    def get_queryset(self):
        return (Post.objects.annotate(comment_count=Count('comments')).filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True).order_by('-pub_date'))


class UserListView(ListView):
    model = Post
    paginate_by = 10
    ordering = '-pub_date'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'blog/profile.html'
    context_object_name = 'profile'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return (Post.objects.annotate(comment_count=Count('comments')).filter(
            author=user).order_by('-pub_date'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs['username'])
        context['profile'] = user
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ('username', 'last_name', 'first_name', 'email',)
    template_name = 'blog/user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_success_url(self, **kwargs):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user})


class PostDetailView(DetailView):
    model = Post
    pk_field = 'post_id'
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        user = self.request.user
        if post.is_published is False and user != post.author:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, id=self.kwargs['post_id'])
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.filter(
            post=self.kwargs['post_id'])
        return context


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    pk_field = 'post_id'
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        if not self.request.user.is_authenticated:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        if post.author != self.request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})


class PostDeleteView(DeleteView):
    model = Post
    from_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    pk_field = 'post_id'
    success_url = 'posts/<post_id>'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        user = self.request.user
        if user != post.author and user.is_superuser is False:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form = PostForm(instance=instance)
        context['form'] = form
        return context

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user})


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    slug_url_kwarg = 'category_slug'
    slug_field = 'category_slug'
    ordering = '-pub_date'
    paginate_by = 10

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

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class CommentDeleteView(DeleteView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
    pk_field = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, id=self.kwargs['comment_id'])
        user = self.request.user
        if user != comment.author and user.is_superuser is False:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class CommentUpdateView(UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
    pk_field = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, id=self.kwargs['comment_id'])
        if comment.author != self.request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})
