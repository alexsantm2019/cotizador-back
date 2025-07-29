from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Producto
from .models import Inventario
from django.db import models 
from .serializers import InventarioSerializer
from productos.serializers import ProductoSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
import datetime
import json
from rest_framework.parsers import JSONParser

@api_view(['GET'])
def get_inventario(request):
    # Filtra los inventarios activos (sin deleted_at)
    inventarios = Inventario.objects.filter(deleted_at__isnull=True)

    # Serializa los inventarios junto con los productos relacionados
    serializer = InventarioSerializer(inventarios, many=True, context={'request': request})
    return JsonResponse(serializer.data, safe=False)

    
def get_inventario1(request):
    # Trae todos los productos con tipo_costo=1 y estado activo
    productos = Producto.objects.filter(tipo_costo=1, deleted_at__isnull=True)

    # Usa prefetch_related para hacer un LEFT JOIN con Inventario
    productos_con_inventario = productos.prefetch_related(
        # Aquí prefetchamos la relación de inventario con los productos
        # Esto hará que aunque no haya registros en Inventario, se devuelvan productos
        # con una lista vacía en el campo inventario
        models.Prefetch('inventarios', queryset=Inventario.objects.filter(deleted_at__isnull=True))
    )

    # Serializa los productos con su inventario asociado
    serializer = ProductoSerializer(productos_con_inventario, many=True, context={'request': request})

    return JsonResponse(serializer.data, safe=False)

# @api_view(['GET'])
# def get_productos_inventario(request):
#     productos = Producto.objects.filter(tipo_costo=1,deleted_at__isnull=True)
#     serializer = ProductoSerializer(productos, many=True, context={'request': request})  # Agregar contexto
#     return JsonResponse(serializer.data, safe=False) 

# @api_view(['POST'])
# def create_producto(request):	
#     if request.method == 'POST':
#         # serializer = ProductoSerializer(data=request.data)
#         serializer = ProductoSerializer(data=request.data, context={'request': request})    # Para agregar user_id
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

# @api_view(['PUT'])
# def update_producto(request, producto_id):
#     try:
#         producto = Producto.objects.get(pk=producto_id)
#     except Producto.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)

#     if request.method == 'PUT':
#         # serializer = ProductoSerializer(producto, data=request.data, context={'action': 'update'})
#         serializer = ProductoSerializer(producto, data=request.data, context={'request': request}, partial=(request.method == 'PATCH')) # Para agregar user_id
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['DELETE'])
# def delete_producto(request, producto_id):
#     try:
#         producto = Producto.objects.get(pk=producto_id)
#     except Producto.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)

#     # Cambiar el estado del producto a eliminado
#     now = datetime.datetime.now()
#     producto.deleted_at  = now
#     producto.save()
#     return Response(status=status.HTTP_204_NO_CONTENT) 
 