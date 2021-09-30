from django import forms

from .models import Comment, Group, Post

HELP_TEXTS_POST = {
    'text': 'Введите текст поста',
    'group': 'Выберите сообщество',
    'image': 'Выберите картинку'
}

HELP_TEXTS_COMMENT = {
    'text': 'Введите текст комментария',
}


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        help_texts = HELP_TEXTS_POST

    def clean_text(self):
        text = self.cleaned_data['text']
        if text is None:
            raise forms.ValidationError('Напишите что-нибудь')
        return text

    def cleaned_group(self):
        group = self.cleaned_data['group']
        if group and Group.objects.filter(pk=group).count() == 0:
            raise forms.ValidationError('Группа не существует')
        return group


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        help_texts = HELP_TEXTS_COMMENT

    def clean_text(self):
        text = self.cleaned_data['text']
        if text is None:
            raise forms.ValidationError('Напишите что-нибудь')
        return text
