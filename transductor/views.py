from django.http import HttpRequest

from django.shortcuts import render
from rest_framework import serializers, viewsets, mixins

from .models import EnergyTransductor

from transductor_model.models import TransductorModel

from .serializers import EnergyTransductorSerializer
from .serializers import ActiveTransductorsSerializer
from .serializers import BrokenTransductorsSerializer


class EnergyTransductorViewSet(viewsets.ModelViewSet):
    queryset = EnergyTransductor.objects.all()
    serializer_class = EnergyTransductorSerializer

    def create(self, request, *args, **kwargs):
        transductor_model = TransductorModel.objects.get(name=request.data['model'])

        print('#########################')
        print(serializer.data['model'])
        print('#########################')

        super().create(request, *args, **kwargs)

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
