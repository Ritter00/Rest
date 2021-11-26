from django.contrib import admin
from .models import *
from modeltranslation.admin import TranslationAdmin

# функция обнуления рейтинга
def rating_null(modeladmin, request, queryset):
    #  request — объект хранящий информацию о запросе и queryset — грубо говоря набор объектов, которых мы выделили галочками.
    queryset.update(rating=0)
rating_null.short_description = 'Обнулить рейтинг поста' #  описание для более понятного представления в админ панеле задаётся, как будто это объект


# создаём новый класс для представления товаров в админке
class PostAdmin(TranslationAdmin):  #  class PostAdmin(admin.ModelAdmin
    # list_display — это список или кортеж со всеми полями, которые вы хотите видеть в таблице с товарами
    # генерируем список имён всех полей для более красивого отображения
    #  list_display = [field.name for field in Post._meta.get_fields()]
    list_display = ('title', 'author', 'rating', 'categoryType', 'dateCreation', 'preview', 'get_absolute_url' )
    #  можно добавлять поля и свойства
    list_filter = ('author', 'dateCreation', 'categoryType', 'title')
    # добавляем примитивные фильтры в нашу админку
    search_fields = ('title',) #  поиск
    actions = [rating_null]  # добавляем действия в список
    model=Post
admin.site.register(Post, PostAdmin)
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(PostCategory)
admin.site.register(SignUser)

