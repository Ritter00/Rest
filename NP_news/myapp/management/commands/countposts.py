from django.core.management.base import BaseCommand, CommandError
from myapp.models import Post

class Command(BaseCommand):
    help = "Считаем количество постов"  # показывает подсказку при вводе "python manage.py <ваша команда> --help"
    requires_migrations_checks = True  # напоминать ли о миграциях. Если тру — то будет напоминание о том, что не сделаны все миграции (если такие есть)

    def handle(self, *args, **options):
        # здесь можете писать любой код, который выполнется при вызове вашей команды
        self.stdout.write("Хотите узать количество статей? yes/no")
        # спрашиваем пользователя о чем-то
        answer = input()  # его ответ

        if answer == 'yes':
            count = len(Post.objects.all())
            return self.stdout.write(self.style.SUCCESS(str(count)))
            # выводим ответ в str
        self.stdout.write(self.style.ERROR('Что-то не то'))  #  в случае неправильного подтверждения

# self.style.SUCCESS(), self.style.ERROR() расцвечивает, можно без этого
# для запуска - python manage.py countposts или  "python manage.py <ваша команда/имя файла>"