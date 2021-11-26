from .models import Post
from modeltranslation.translator import register, TranslationOptions
# импортируем декоратор для перевода и класс настроек, от которого будем наследоваться


@register(Post)    # регистрируем наши модели для перевода
class PostTranslationOptions(TranslationOptions):
    fields = ('text','title')   # указываем, какие именно поля надо переводить в виде кортежа

