from django.apps import AppConfig


class TransductorConfig(AppConfig):
    name = 'transductor'
    api = None

    def ready(self):
        from . import api
        self.api = api
