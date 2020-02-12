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
    queryset = VoltageRelatedEvent.objects.none()
    models = {
        'FailedConnectionTransductorEvent': FailedConnectionTransductorEvent,
        'CriticalVoltageEvent': CriticalVoltageEvent,
        'PrecariousVoltageEvent': PrecariousVoltageEvent,
        'PhaseDropEvent': PhaseDropEvent
    }

    def list(self, request):
        # The period is defined by each minute because the collection for the
        # measurement related is defined by each minute too.
        types = list(self.models.keys())

        events = []
        for type in types:
            last_event = VoltageRelatedEvent.objects.instance_of(
                self.models[type]
            ).last()

            if last_event:
                data = {}
                data['data'] = {}
                for measure in last_event.data.keys():
                    data['data'].setdefault(measure)
                    data['data'].update({measure: last_event.data[measure]})

                data['ip_address'] = last_event.transductor.ip_address
                data['created_at'] = last_event.created_at
                data['ended_at'] = last_event.ended_at
                data['type'] = last_event.__class__.__name__
                events.append(data)

        return Response(events, status=200)


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
