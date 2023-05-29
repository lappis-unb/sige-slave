from rest_framework.viewsets import ModelViewSet

from data_collector.models import MemoryMap
from data_collector.serializers import MemoryMapSerializer


class MemoryMapViewSet(ModelViewSet):
    queryset = MemoryMap.objects.all()
    serializer_class = MemoryMapSerializer
