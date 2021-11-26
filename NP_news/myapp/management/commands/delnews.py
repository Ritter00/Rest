from django.core.management.base import BaseCommand, CommandError
from myapp.models import Post, Category

class Command(BaseCommand):
    help = 'Удаляем все посты в категории'


    def handle(self, *args, **options):
        allcat = Category.objects.all()
        _list = []

        for i in allcat:
            _list.append(i.category)
        self.stdout.write("Укажите категорию")
        cat = ' - '.join(_list)
        self.stdout.write(str(cat))
        ans = input()
        if ans in _list:
            self.stdout.write(f"Вы хотите удалить все новости в категори {ans} y/n")
            ans1 = input()
            if ans1 == 'y':
                catdel = Category.objects.get(category=ans)
                posts= Post.objects.filter(postCategory=catdel.id)
                #for post in posts:
                    #post.delete()

            return self.stdout.write(self.style.SUCCESS(f'есть такое {posts}'))
        self.stdout.write(self.style.ERROR('Что-то не то'))