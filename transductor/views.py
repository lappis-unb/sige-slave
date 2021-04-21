from rest_framework import mixins, viewsets

from .models import EnergyTransductor
from .serializers import (ActiveTransductorsSerializer,
                          BrokenTransductorsSerializer,
                          EnergyTransductorSerializer)


class EnergyTransductorViewSet(viewsets.ModelViewSet):
    queryset = EnergyTransductor.objects.all()
    serializer_class = EnergyTransductorSerializer


class ActiveTransductorsViewSet(mixins.RetrieveModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    queryset = EnergyTransductor.objects.all()
    serializer_class = ActiveTransductorsSerializer


class BrokenTransductorsViewSet(mixins.RetrieveModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    queryset = EnergyTransductor.objects.all()
    serializer_class = BrokenTransductorsSerializer
