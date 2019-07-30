from rest_framework import serializers, viewsets, mixins

from .models import EnergyTransductor
from .serializers import EnergyTransductorSerializer
from .serializers import ActiveTransductorsSerializer
from .serializers import BrokenTransductorsSerializer


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
