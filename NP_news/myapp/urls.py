from django.urls import path
from .views import PostList, PostDetail, PostListSearch, PostCreateView, PostUpdateView, PostDeleteView
from .views import upgrade_me, CategoryList, CategoryDetail, subscriber, Index

from django.views.decorators.cache import cache_page

urlpatterns = [
    path('', cache_page(1)(PostList.as_view())),
    path('<int:pk>', PostDetail.as_view(), name='post_detail'),
    path('search/', PostListSearch.as_view()),
    path('create/', PostCreateView.as_view(), name='post_create'),
    path('create/<int:pk>', PostUpdateView.as_view(), name='post_update'),
    path('delete/<int:pk>', PostDeleteView.as_view(), name='post_delete'),
    path('create/upgrade/', upgrade_me, name='upgrade'),
    path('category/', cache_page(60 * 5)(CategoryList.as_view()), name='categories'),
    #  Кэшируем список категорий на 5 мин (60 секунд * 5)
    path('category/<int:pk>', CategoryDetail.as_view(), name='category_detail'),
    path('category/<int:pk>/', subscriber, name='subscriber'),
    path('test/', Index.as_view())

]
