from django.apps import AppConfig


class MeasurementConfig(AppConfig):
    name = 'measurement'
    api = None

    def ready(self):
        from . import api
        self.api = api
