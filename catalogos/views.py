from django.shortcuts import render

# Create your views here.
# Create your views here.
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Catalogo
from .serializers import CatalogoSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
import datetime
import json
from rest_framework.parsers import JSONParser

@api_view(['GET'])
def get_catalogo_by_grupo(request, grupo):
    try:
        # Filtrar los productos por el grupo numérico
        catalogo = Catalogo.objects.filter(grupo=grupo).order_by('item')  # Filtrar por grupo numérico
        
        if catalogo.exists():
            serializer = CatalogoSerializer(catalogo, many=True)
            return Response(serializer.data)
        else:
            return Response({"detail": "No se encontraron productos para este grupo."}, status=status.HTTP_404_NOT_FOUND)
    
    except ValueError:
        return Response({"detail": "El parámetro 'grupo' debe ser un número."}, status=status.HTTP_400_BAD_REQUEST)
