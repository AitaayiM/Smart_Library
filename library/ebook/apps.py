from django.apps import AppConfig


class EbookConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ebook'
    def ready(self):
        import ebook.signals
        