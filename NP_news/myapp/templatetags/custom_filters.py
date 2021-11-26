from django import template

register = template.Library()

@register.filter(name='censor')
def censor(value):
    cens_words = [
        'сторис',
        'подушка',
        'вещей',
        'Джо',
    ]
    for word in cens_words:
        if word in value:
            value = value.replace(word, '_#&#!!*&$_')
    return value

