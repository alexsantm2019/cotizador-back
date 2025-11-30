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
        catalogo = Catalogo.objects.filter(grupo=grupo, deleted_at__isnull=True).order_by('codigo', 'item')  # Filtrar por grupo numérico
        
        if catalogo.exists():
            serializer = CatalogoSerializer(catalogo, many=True)
            return Response(serializer.data)
        else:
            return Response({"detail": "No se encontraron catalogos para este grupo."}, status=status.HTTP_404_NOT_FOUND)
    
    except ValueError:
        return Response({"detail": "El parámetro 'grupo' debe ser un número."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_catalogo_by_nombre(request, nombre):
    try:
        # Filtrar coincidencias parciales en cualquier parte del texto
        catalogo = Catalogo.objects.filter(
            detalle__icontains=nombre,
            deleted_at__isnull=True
        ).order_by('codigo', 'item')

        if catalogo.exists():
            serializer = CatalogoSerializer(catalogo, many=True)
            return Response(serializer.data)
        else:
            return Response({"detail": "No se encontraron catálogos que coincidan con el texto buscado."},
                            status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"detail": "Error en la búsqueda: " + str(e)}, 
                        status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_catalogos(request):
    """Obtiene todos los registros del catálogo con deleted_at = NULL"""
    catalogos = Catalogo.objects.order_by('grupo')
    serializer = CatalogoSerializer(catalogos, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_catalogos_activos(request):
    """Obtiene todos los registros del catálogo con deleted_at = NULL"""
    catalogos = Catalogo.objects.filter(deleted_at__isnull=True).order_by('grupo','codigo')
    serializer = CatalogoSerializer(catalogos, many=True)
    return Response(serializer.data)        

@api_view(['DELETE'])
def eliminar_catalogo(request, id):
    """Marca como eliminado un registro del catálogo usando deleted_at"""
    try:
        catalogo = Catalogo.objects.get(id=id, deleted_at__isnull=True)
        catalogo.deleted_at = timezone.now()
        catalogo.save()
        return Response({"detail": "Catálogo eliminado correctamente."}, status=status.HTTP_200_OK)
    except Catalogo.DoesNotExist:
        return Response({"detail": "El catálogo no existe o ya fue eliminado."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def crear_catalogo(request):
    """Crea un nuevo registro en el catálogo"""
    serializer = CatalogoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    


@api_view(['PUT'])
def update_catalogo(request, catalogo_id):
    try:
        catalogo = Catalogo.objects.get(id=catalogo_id, deleted_at__isnull=True)
    except Catalogo.DoesNotExist:
        return Response({"detail": "Registro no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = CatalogoSerializer(catalogo, data=request.data, context={'request': request}, partial=(request.method == 'PATCH')) # Para agregar user_id
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
