from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from data_collector.modbus.settings import CSV_DIR_PATH
from data_collector.serializers import MemoryMapSerializer
from transductor.models import Transductor
from transductor.serializers import (
    ActiveTransductorsSerializer,
    BrokenTransductorsSerializer,
    TransductorSerializer,
)


class TransductorViewSet(viewsets.ModelViewSet):
    queryset = Transductor.objects.all()
    serializer_class = TransductorSerializer

    def create(self, request, *args, **kwargs):
        model = request.data.get("model")

        if not model:
            return Response({"error": "Model field is required"}, status=400)

        csv_filename = request.data.get("model").lower().strip().replace(" ", "_")
        csv_file_path = (CSV_DIR_PATH / csv_filename).with_suffix(".csv")

        if not csv_file_path.exists():
            return Response({"error": f"Memory Map not found in CSV file for model: {model}"}, status=400)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    @action(detail=True, methods=["get"], url_path="memory-map")
    def memorymap(self, request, pk=None):
        transductor = self.get_object()
        serializer = MemoryMapSerializer(transductor.memory_map)
        return Response(serializer.data)


class ActiveTransductorsViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Transductor.objects.all()
    serializer_class = ActiveTransductorsSerializer


class BrokenTransductorsViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Transductor.objects.all()
    serializer_class = BrokenTransductorsSerializer
