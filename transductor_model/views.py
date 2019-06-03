import jwt as JWT

from django.shortcuts import render
from rest_framework import viewsets
from django.conf import LazySettings
from rest_framework import serializers
from rest_framework.response import Response
from django.http import HttpResponseForbidden

from .models import TransductorModel
from .serializers import TransductorModelSerializer


settings = LazySettings()


class TransductorModelViewSet(viewsets.ModelViewSet):
    queryset = TransductorModel.objects.all()
    serializer_class = TransductorModelSerializer

    # def _verify_jwt(self, token):
    #     jwt = JWT()
    #     try:
    #         data = jwt.decode(token, settings.SECRET_KEY)
    #         return data
    #     except Exception:
    #         return None

    # def create(self, request):
    #     data = self._verify_jwt(request.body['msg'])
    #     if data is None:
    #         return Response({'error': 'invalid or unexistent comms token'},
    #                         status=403)
    #     else:
    #         print("=================")
    #         print(data)
    #         print("=================")

    #         # super(TransductorModelViewSet, self).create(self, data)

    # def update(self, request, pk=None):
    #     data = self._verify_jwt(request.body['msg'])
    #     if data is not True:
    #         return Response({'error': 'invalid or unexistent comms token'},
    #                         status=403)
    #     else:
    #         super(TransductorModelViewSet, self).update(self, data, pk)

    # def partial_update(self, request, pk=None):
    #     data = self._verify_jwt(request.body['msg'])
    #     if data is not True:
    #         return Response({'error': 'invalid or unexistent comms token'},
    #                         status=403)
    #     else:
    #         super(TransductorModelViewSet, self).partial_update(
    #             self, data, pk)

    # def destroy(self, request, pk=None):
    #     data = self._verify_jwt(request.body['msg'])
    #     if data is not True:
    #         return Response({'error': 'invalid or unexistent comms token'},
    #                         status=403)
    #     else:
    #         super(TransductorModelViewSet, self).destroy(self, data, pk)
