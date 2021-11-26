from django_filters import FilterSet, DateFilter, CharFilter # импортируем filterset, чем-то напоминающий знакомые дженерики
from .models import *
from django import forms

class PostFilter(FilterSet):# создаём фильтр
    date = DateFilter(
        field_name='dateCreation',
        widget= forms.DateInput(attrs={'type': 'date', }),
        lookup_expr='gte',

    )
# widget= forms.TextInput(attrs={'placeholder': 'Название', 'class' : 'form-control'}) - поле на всю ширину
    title = CharFilter(
        field_name= 'title',
        widget= forms.TextInput(attrs={
            'placeholder': 'Название',
        }),
        lookup_expr='icontains',
    )


# Здесь в мета классе надо предоставить модель и указать поля, по которым будет фильтроваться (т. е. подбираться) информация о товарах
    class Meta:
        model = Post
        fields= ['date', 'title','author',]  #author__authorUser__username - доступ к норм. названию

