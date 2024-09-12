from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Définir les paramètres de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library.settings')

app = Celery('library')
# Utiliser une chaîne de configuration depuis les paramètres de Django
app.config_from_object('django.conf:settings', namespace='CELERY')
# Découvrir automatiquement les tâches des applications Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
    