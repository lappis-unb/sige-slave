from django.shortcuts import render

from rest_framework import serializers, viewsets, mixins

from .models import EnergyTransductor
from .serializers import EnergyTransductorSerializer
from .serializers import ActiveTransductorsSerializer


class EnergyTransductorViewSet(viewsets.ModelViewSet):
    queryset = EnergyTransductor.objects.all()
    serializer_class = EnergyTransductorSerializer

class ActiveTransductorsViewSet(mixins.RetrieveModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    serializer_class = ActiveTransductorsSerializer
    queryset = EnergyTransductor.objects.all()
    