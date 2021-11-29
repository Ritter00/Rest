from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from .models import Post, Category, SignUser, User
from .filters import PostFilter
from django.shortcuts import render, redirect, reverse
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from .tasks import send_mail
from django.core.cache import cache
import logging
from django.utils.translation import gettext as _
from django.utils import timezone
import pytz
from rest_framework import viewsets, permissions
from .serializers import *
from rest_framework.response import Response

logger = logging.getLogger(__name__)  #  регистрация логгирования


class PostList(ListView):
    model = Post
    template_name = 'posts.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-id')  # сортируем, еще можно через ordering = ['-id']
    paginate_by = 5  # поставим постраничный вывод в n-элемент
    form_class = PostForm
    curent_time = timezone.now()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(
            **kwargs)  # забираем отфильтрованные объекты переопределяя метод get_context_data у наследуемого класса
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        context['form'] = PostForm()
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        context['current_time'] = timezone.now()
        context['timezones'] = pytz.common_timezones  #  добавляем в контекст все доступные часовые пояса

        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        request.session['django_timezone'] = request.POST['timezone']

        if form.is_valid():
            form.save()

        return super().get(request, *args, **kwargs)


class PostDetail(DetailView):
    # model = Post
    # template_name = 'post.html'
    # context_object_name = 'post'
    template_name = 'post_detail.html'
    queryset = Post.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        models = Post.objects.all()
        de = kwargs['object'].postCategory
        context['models'] = models
        context['pop'] = de.all().last().subscribers.all()
        return context

    def get_object(self, *args, **kwargs):  # переопределяем метод получения объекта, как ни странно
        obj = cache.get(f'post-{self.kwargs["pk"]}', None)
        # кэш очень похож на словарь, и метод get действует также.
        # Он забирает значение по ключу, если его нет, то забирает None.
        #  если объекта нет в кэше, то получаем его и записываем в кэш
        if not obj:
            obj = super().get_object(*args, **kwargs)
            cache.set(f'post-{self.kwargs["pk"]}', obj)

        return obj


class PostListSearch(ListView, ):
    model = Post
    template_name = 'posts_search.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-id')  # сортируем, еще можно через ordering = ['-id']
    paginate_by = 10  # поставим постраничный вывод в n-элемент

    def get_filter(self):
        return PostFilter(self.request.GET, queryset=super().get_queryset())

    def get_queryset(self):
        return self.get_filter().qs

    def get_context_data(self, *args, **kwargs):
        return {
            **super().get_context_data(*args, **kwargs),
            'filter': self.get_filter(),
        }


class PostCreateView(PermissionRequiredMixin, CreateView):
    template_name = 'post_create.html'
    permission_required = ('myapp.add_post',)
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context

    def form_valid(self, form):  # для сигнала, сохраняем обьект дважды, дважды сиганалит
        self.object = form.save()
        pk = self.request.POST['postCategory']
        url = f'{self.object.get_absolute_url()}'
        cat = Category.objects.get(id=pk).subscribers.all()
        mail = []
        post = f'{self.object.text}'
        cate = f'{Category.objects.get(id=pk).category}'
        for subscriber in cat:
            mail.append(subscriber.email)
        #  send_mail.delay(mail, post, cate, url)  # вызываем таск
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'post_create.html'
    permission_required = ('myapp.change_post')
    form_class = PostForm

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context


class PostDeleteView(DeleteView):
    template_name = 'post_delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'


@login_required
def upgrade_me(request):
    user = request.user
    author_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        author_group.user_set.add(user)
    return redirect('/')


class CategoryList(ListView):
    model = Category
    template_name = 'categories.html'
    context_object_name = 'categories'


class CategoryDetail(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'category_detail.html'
    queryset = Category.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['if_not_subscriber'] = Category.objects.filter(id=kwargs['object'].id, subscribers=self.request.user)
        us = Category.objects.get(id=kwargs['object'].id)
        context['if_not_subscriber'] = us.subscribers.filter(id=self.request.user.id).last()
        context['re'] = us.subscribers.all()
        return context


def subscriber(request, pk):
    user = request.user.id
    sub_user = User.objects.get(id=user)
    cat = Category.objects.get(id=pk)
    if cat.subscribers.filter(id=user):
        cat.subscribers.remove(sub_user)
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        cat.subscribers.add(sub_user)
        return redirect(request.META.get('HTTP_REFERER'))


class Index(View):
    def get(self, request):
        string = _('Yo, Hello world')
        return HttpResponse(string, request)


class PostViewSetAR(viewsets.ModelViewSet):
    queryset = Post.objects.filter(categoryType='AR')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PostViewSetNW(viewsets.ModelViewSet):
    queryset = Post.objects.filter(categoryType='NW')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    #def list(self, request, format=None):  # пустой список
        #return Response([])