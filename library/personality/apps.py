from django.apps import AppConfig


class PersonalityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'personality'

    def ready(self):
        import personality.signals
