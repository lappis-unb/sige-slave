from rest_framework import viewsets
from rest_framework import mixins
from .serializers import EventSerializer
from .models import Event
from .models import FailedConnectionEvent
from .models import CriticalVoltageEvent
from .models import PrecariousVoltageEvent
from .models import PhaseDropEvent


class EventViewSet(mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    models = {
        'FailedConnectionEvent': FailedConnectionEvent,
        'CriticalVoltageEvent': CriticalVoltageEvent,
        'PrecariousVoltageEvent': PrecariousVoltageEvent,
        'PhaseDropEvent': PhaseDropEvent
    }

    def get_queryset(self):
        type = self.request.query_params.get('type')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

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
            print('*'*100)
            # print(event.measures)
            data['measures'] = []
            for measure in event.measures.keys():
                data['measures'].append([measure, event.measures[measure]])
                # print(data['measures'][measure])
            # print(data['measures'])
            data['created_at'] = event.created_at
            data['type'] = event.__class__.__name__
            print(data)
            events.append(data)

        return events
