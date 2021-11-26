from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models import  Sum
from allauth.account.forms import SignupForm
from django.core.cache import cache
from django.utils.translation import pgettext_lazy
from django.utils.translation import gettext as _


class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete= models.CASCADE)
    ratingAuthor = models.SmallIntegerField(default=0)

    def update_rating(self):
        postRat = self.post_set.aggregate(postRating=Sum('rating'))
        pRat = 0
        pRat += postRat.get('postRating')

        commentRat = self.authorUser.comment_set.aggregate(commentRating=Sum('rating'))
        cRat = 0
        cRat += commentRat.get('commentRating')

        self.ratingAuthor = pRat * 3 + cRat
        self.save()

    def __str__(self):
        return self.authorUser.username


class SignUser(models.Model):
    sign_user = models.OneToOneField(User,on_delete= models.CASCADE)


class Category(models.Model):
    category = models.CharField(max_length=64, unique= True, help_text=_('category name'))
    subscribers = models.ManyToManyField(
        User, related_name='subscriber',
        verbose_name=pgettext_lazy('help text for MyModel model', 'subscribers')
    )

    def __str__(self): # переопределяем метод, выводиться норм. название
        return self.category

    class Meta:
        verbose_name = 'Категория' # название в админки
        verbose_name_plural = 'Категории' # название во множ. числе в админке
        ordering = ['-id'] # сортировка в админке



class Post(models.Model):
    author = models.ForeignKey(Author, on_delete= models.CASCADE)
    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOICE = (
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья'),
    )
    categoryType = models.CharField(max_length=2,choices= CATEGORY_CHOICE, default= ARTICLE)
    dateCreation = models.DateTimeField(auto_now_add= True)
    postCategory = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=128)
    text = models.TextField()
    rating = models.SmallIntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()


    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[0:123] + '...'

    def __str__(self):
        return f'{self.title}'

    def get_absolute_url(self):
        return f'http://127.0.0.1:8000/news/{self.id}' # добавим абсолютный путь, чтобы после создания нас перебрасывало на страницу с товаром

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # сначала вызываем метод родителя, чтобы объект сохранился
        cache.delete(f'post-{self.pk}') # затем удаляем его из кэша, чтобы сбросить его






class PostCategory(models.Model):
    postThrough = models.ForeignKey(Post, on_delete= models.CASCADE)
    categoryThrough = models.ForeignKey(Category, on_delete= models.CASCADE)


class Comment(models.Model):
    commentPost = models.ForeignKey(Post, on_delete= models.CASCADE)
    commentUser = models.ForeignKey(User, on_delete= models.CASCADE)
    text = models.TextField(verbose_name='Описание') # verbose_name='Описание' название поля в админке
    dateCreation = models.DateTimeField(auto_now_add= True)
    rating = models.SmallIntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()


class BasicSignupForm(SignupForm):
    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        return user