import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPaper.settings')
#  связываем настройки Django с настройками Celery через переменную окружения.
app = Celery('NewsPaper')
app.config_from_object('django.conf:settings', namespace = 'CELERY')
#  создаем экземпляр приложения Celery и устанавливаем для него файл конфигурации. Мы также указываем пространство имен, чтобы Celery сам находил все необходимые настройки в общем конфигурационном файле settings.py. Он их будет искать по шаблону «CELERY_***».

app.autodiscover_tasks()
#  указываем Celery автоматически искать задания в файлах tasks.py каждого приложения проекта.
app.conf.beat_schedule = {
    'spam':{
        'task':'myapp.tasks.spam',
        'schedule': crontab(hour=8, minute=0,day_of_week='monday'),
        'args':(),
            }

}