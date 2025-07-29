from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.http import JsonResponse
from .models import CategoriaProducto
from .serializers import CategoriaProductoSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
import datetime
import json
from rest_framework.parsers import JSONParser

@api_view(['GET'])
def get_categoria_producto(request):
    # categorias = CategoriaProducto.objects.all().order_by('categoria') 
    categorias = CategoriaProducto.objects.filter(deleted_at__isnull=True).order_by('categoria')
    serializer = CategoriaProductoSerializer(categorias, many=True)
    return JsonResponse(serializer.data, safe=False) 

@api_view(['POST'])
def create_categoria_producto(request):    
    if request.method == 'POST':
        serializer = CategoriaProductoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

@api_view(['PUT'])
def update_categoria_producto(request, categoria_id):
    try:
        categoria = CategoriaProducto.objects.get(pk=categoria_id)
    except CategoriaProducto.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = CategoriaProductoSerializer(categoria, data=request.data, context={'action': 'update'})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_categoria_producto(request, categoria_id):
    try:
        categoria = CategoriaProducto.objects.get(pk=categoria_id)
    except CategoriaProducto.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Cambiar el estado del producto a eliminado
    now = datetime.datetime.now()
    categoria.deleted_at  = now
    categoria.save()
    return Response(status=status.HTTP_204_NO_CONTENT) 