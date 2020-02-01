from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response
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

        self.queryset = self.queryset.filter(
            ended_at__isnull=True
        )

        if type:
            self.queryset = self.queryset.instance_of(self.models[type])

        events = []
        for event in self.queryset:
            data = {}
            data['data'] = {}
            for measure in event.data.keys():
                data['data'].setdefault(measure)
                data['data'].update({measure: event.data[measure]})

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
    query = FailedConnectionTransductorEvent.objects.all()

    def list(self, request):
        last_event = None
        # The period is defined by each minute because the collection for the
        # measurement related is defined by each minute too.

        last_event = self.query.last()

        data = {}
        if last_event:
            data['data'] = last_event.data
            data['ip_address'] = last_event.transductor.ip_address
            data['created_at'] = last_event.created_at
            data['ended_at'] = last_event.ended_at
            data['type'] = last_event.__class__.__name__

        return Response(data, status=200)
