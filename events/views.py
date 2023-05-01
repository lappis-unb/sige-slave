from rest_framework import mixins, viewsets
from rest_framework.response import Response

from transductor.models import Transductor

from .models import (
    CriticalVoltageEvent,
    FailedConnectionTransductorEvent,
    PhaseDropEvent,
    PrecariousVoltageEvent,
    VoltageRelatedEvent,
)
from .serializers import (
    FailedConnectionTransductorEventSerializer,
    VoltageRelatedEventSerializer,
)


class VoltageRelatedEventViewSet(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = VoltageRelatedEventSerializer
    queryset = VoltageRelatedEvent.objects.none()
    models = {
        "CriticalVoltageEvent": CriticalVoltageEvent,
        "PrecariousVoltageEvent": PrecariousVoltageEvent,
        "PhaseDropEvent": PhaseDropEvent,
    }

    def list(self, request):
        # The period is defined by each minute because the collection for the
        # measurement related is defined by each minute too.
        types = list(self.models.keys())

        events = []
        for transductor in Transductor.objects.all():
            for type in types:
                last_event = transductor.events_event.instance_of(self.models[type]).last()

                if last_event:
                    data = {}
                    data["data"] = {}
                    for measure in last_event.data.keys():
                        data["data"][measure] = last_event.data[measure]

                    data["ip_address"] = last_event.transductor.ip_address
                    data["created_at"] = last_event.created_at
                    data["ended_at"] = last_event.ended_at
                    data["type"] = last_event.__class__.__name__
                    events.append(data)

        return Response(events, status=200)


class FailedConnectionTransductorEventViewSet(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = FailedConnectionTransductorEventSerializer
    queryset = FailedConnectionTransductorEvent.objects.none()

    def list(self, request):
        events = []
        # The period is defined by each minute because the collection for the
        # measurement related is defined by each minute too.

        for transductor in Transductor.objects.all():
            last_event = transductor.events_event.instance_of(FailedConnectionTransductorEvent).last()

            if last_event:
                data = {}
                data["data"] = last_event.data
                data["ip_address"] = last_event.transductor.ip_address
                data["created_at"] = last_event.created_at
                data["ended_at"] = last_event.ended_at
                data["type"] = last_event.__class__.__name__
                events.append(data)

        return Response(events, status=200)
