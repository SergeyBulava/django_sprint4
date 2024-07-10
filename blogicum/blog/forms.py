from .models import Post, Comment
from django import forms


class PostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        label='Дата и время публикации',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = Post
        exclude = ('author', )


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
