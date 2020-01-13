from rest_framework import viewsets
from rest_framework import mixins
from .serializers import VoltageRelatedEventSerializer
from .serializers import FailedConnectionTransductorEventSerializer
from .models import VoltageRelatedEvent
from .models import FailedConnectionTransductorEvent
from .models import CriticalVoltageEvent
from .models import PrecariousVoltageEvent
from .models import PhaseDropEvent
from django.utils import timezone


class VoltageRelatedEventViewSet(mixins.RetrieveModelMixin,
                                 mixins.DestroyModelMixin,
                                 mixins.ListModelMixin,
                                 viewsets.GenericViewSet):
    serializer_class = VoltageRelatedEventSerializer
    queryset = VoltageRelatedEvent.objects.all()
    models = {
        'FailedConnectionTransductorEvent': FailedConnectionTransductorEvent,
        'CriticalVoltageEvent': CriticalVoltageEvent,
        'PrecariousVoltageEvent': PrecariousVoltageEvent,
        'PhaseDropEvent': PhaseDropEvent
    }

    def get_queryset(self):
        type = self.request.query_params.get('type')
        # The period is defined by each minute because the collection for the
        # measurement related is defined by each minute too.
        now = timezone.now()
        start_date = timezone.datetime(
            now.year, now.month, now.day, now.hour-1, now.minute, 0, 0
        )
        end_date = timezone.datetime(
            now.year, now.month, now.day, now.hour-1, now.minute, 59, 999999
        )

        if start_date and end_date:
            self.queryset = self.queryset.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            )

        if type:
            self.queryset = self.queryset.instance_of(self.models[type])

        events = []
        for event in self.queryset:
            data = {}
            data['measures'] = {}
            for measure in event.measures.keys():
                data['measures'].setdefault(measure)
                data['measures'].update({measure: event.measures[measure]})

            data['ip_address'] = event.transductor.ip_address
            data['created_at'] = event.created_at
            data['ended_at'] = event.ended_at
            data['type'] = event.__class__.__name__
            events.append(data)

        return events


class FailedConnectionTransductorEventViewSet(mixins.RetrieveModelMixin,
                                   mixins.DestroyModelMixin,
                                   mixins.ListModelMixin,
                                   viewsets.GenericViewSet):
    serializer_class = FailedConnectionTransductorEventSerializer
    queryset = FailedConnectionTransductorEvent.objects.all()

    def get_queryset(self):
        type = self.request.query_params.get('type')
        # The period is defined by each minute because the collection for the
        # measurement related is defined by each minute too.
        now = timezone.now()
        start_date = now - timezone.timedelta(minutes=1)
        end_date = now

        if start_date and end_date:
            self.queryset = self.queryset.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            )

        if type:
            self.queryset = self.queryset.instance_of(self.models[type])

        events = []
        for event in self.queryset:
            data = {}
            data['ip_address'] = event.transductor.ip_address
            data['created_at'] = event.created_at
            data['ended_at'] = event.ended_at
            data['type'] = event.__class__.__name__
            events.append(data)

        return events
