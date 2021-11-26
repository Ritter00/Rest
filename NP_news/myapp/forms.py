from django.forms import ModelForm
from .models import Post
from django import forms

# Создаём модельную форму
class PostForm(ModelForm):


# в класс мета, как обычно, надо написать модель, по которой будет строится форма и нужные нам поля. Мы уже делали что-то похожее с фильтрами.
    class Meta:
        model = Post
        fields = ['author','title', 'categoryType', 'postCategory', 'text']
        widgets = {
            'text' : forms.Textarea(attrs={'cols': 150, 'rows': 5}),
                   }

