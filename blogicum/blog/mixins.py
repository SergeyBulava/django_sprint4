from django.shortcuts import redirect


class DispatchMixin:

    def dispatch(self, request, *args, **kwargs):
        post = super().get_object()
        if post.author != self.request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)
