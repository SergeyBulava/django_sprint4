from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        label='Дата и время публикации',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = Post
        exclude = ('author',)


class CommentForm(forms.ModelForm):
    text = forms.CharField(label='Текст комментария',
                           widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = Comment
        fields = ('text',)
