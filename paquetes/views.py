from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Paquete, PaqueteDetalle
from .serializers import PaqueteSerializer
from .serializers import PaqueteDetalleSerializer
from productos.models import Producto
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
import datetime
import json
from rest_framework.parsers import JSONParser
from categoria_producto.models import CategoriaProducto
from django.shortcuts import get_object_or_404
from django.db import transaction

@api_view(['GET'])
def get_paquetes(request):
    paquetes = Paquete.objects.all()  # Trae todos los paquetes
    paquetes_data = []
    for paquete in paquetes:
        # Serializar detalles del paquete
        detalles = PaqueteDetalle.objects.filter(paquete=paquete)
        detalles_serializados = [
            {
                "id": detalle.id,
                "producto": {
                    "id": detalle.producto.id,  # ID del producto
                    "producto": detalle.producto.producto,  # Nombre del producto
                    "descripcion": detalle.producto.descripcion,  # Descripción del producto
                    "tipo_costo": detalle.producto.tipo_costo,  # Tipo de costo del producto (1 o 2)
                    "costo": detalle.producto.costo,
                },
                "cantidad": detalle.cantidad,
                "duracion_horas": detalle.duracion_horas,
                "costo_producto": str(detalle.costo_producto),  # Convierte a string para evitar problemas de JSON
            }
            for detalle in detalles
        ]
        paquetes_data.append({
            "id": paquete.id,
            "nombre_paquete": paquete.nombre_paquete,
            "descripcion": paquete.descripcion,
            "precio_total": str(paquete.precio_total),  # Convertir a string
            "estado": paquete.estado,
            "detalles": detalles_serializados,
        })
    return Response(paquetes_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_paquete_by_id(request, paquete_id):
    try:
        paquete = Paquete.objects.get(pk=paquete_id)  # Buscar el paquete por ID
    except Paquete.DoesNotExist:
        return Response({"error": "Paquete no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    # Serializar detalles del paquete
    detalles = PaqueteDetalle.objects.filter(paquete=paquete)
    detalles_serializados = [
        {
            "id": detalle.id,
            "producto": {
                "id": detalle.producto.id,  # ID del producto
                "producto": detalle.producto.producto,  # Nombre del producto
                "descripcion": detalle.producto.descripcion,  # Descripción del producto
                "tipo_costo": detalle.producto.tipo_costo,  # Tipo de costo del producto (1 o 2)
                "costo": detalle.producto.costo,
            },
            "cantidad": detalle.cantidad,
            "duracion_horas": detalle.duracion_horas,
            "costo_producto": str(detalle.costo_producto),  # Convertir a string para evitar problemas de JSON           
        }
        for detalle in detalles
    ]
    paquete_data = {
        "id": paquete.id,
        "nombre_paquete": paquete.nombre_paquete,
        "descripcion": paquete.descripcion,
        "precio_total": str(paquete.precio_total),  # Convertir a string
        "estado": paquete.estado,
        "categoria_producto_id": paquete.categoria_producto_id.id if paquete.categoria_producto_id else None,  # Acceder al id de CategoriaProducto
        "detalles": detalles_serializados,
    }

    # Devolver el paquete como un único elemento dentro de un array
    return Response([paquete_data], status=status.HTTP_200_OK)


@api_view(['POST'])
def create_paquete(request):
    detalles_data = request.data.pop('detalles', [])
    # Si no se proporciona precio_total, se asigna 0
    precio_total = request.data.get('precio_total', 0)

   # Obtener la instancia de CategoriaProducto
    categoria_producto_id = request.data.get('categoria_producto_id')
    categoria_producto = None
    if categoria_producto_id:  # Validar que no sea None
        categoria_producto = get_object_or_404(CategoriaProducto, pk=categoria_producto_id)

    paquete = Paquete.objects.create(
        nombre_paquete=request.data.get('nombre_paquete'),
        descripcion=request.data.get('descripcion'),
        categoria_producto_id=categoria_producto,
        # precio_total=request.data.get('precio_total'),
        precio_total=precio_total, 
        estado=request.data.get('estado', 1)
    )
    for detalle_data in detalles_data:
        producto_id = detalle_data.pop('producto')
        producto = Producto.objects.get(pk=producto_id)  # Convierte el ID en instancia
        PaqueteDetalle.objects.create(paquete=paquete, producto=producto, **detalle_data)
    return Response({"message": "Paquete creado con éxito"}, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@transaction.atomic  # Utilizamos el decorador para manejar la transacción
def update_paquete(request, paquete_id):
    try:
        # Obtener el paquete que queremos actualizar
        paquete = Paquete.objects.get(pk=paquete_id)
    except Paquete.DoesNotExist:
        return Response({"error": "Paquete no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    # Eliminar todos los detalles existentes del paquete
    PaqueteDetalle.objects.filter(paquete=paquete).delete()

    # Obtener los datos de los detalles y otros campos
    detalles_data = request.data.pop('detalles', [])
    precio_total = request.data.get('precio_total', 0)

    # Obtener la instancia de CategoriaProducto (si se proporciona)
    categoria_producto_id = request.data.get('categoria_producto_id')
    categoria_producto = None
    if categoria_producto_id:  # Validar que no sea None
        categoria_producto = get_object_or_404(CategoriaProducto, pk=categoria_producto_id)

    # Actualizar los campos del paquete
    paquete.nombre_paquete = request.data.get('nombre_paquete', paquete.nombre_paquete)
    paquete.descripcion = request.data.get('descripcion', paquete.descripcion)
    paquete.categoria_producto_id = categoria_producto
    paquete.precio_total = precio_total
    paquete.estado = request.data.get('estado', paquete.estado)
    paquete.save()  # Guardar los cambios del paquete

    # Crear los nuevos detalles para el paquete
    for detalle_data in detalles_data:
        producto_id = detalle_data.pop('producto')
        producto = Producto.objects.get(pk=producto_id)  # Convierte el ID en instancia
        PaqueteDetalle.objects.create(paquete=paquete, producto=producto, **detalle_data)

    return Response({"message": "Paquete actualizado con éxito"}, status=status.HTTP_200_OK)   

@api_view(['DELETE'])
def delete_paquete(request, paquete_id):
    try:
        # Obtener el paquete
        paquete = Paquete.objects.get(pk=paquete_id)
    except Paquete.DoesNotExist:
        return Response({"error": "Paquete no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    try:
        # Eliminar todos los detalles asociados al paquete
        PaqueteDetalle.objects.filter(paquete=paquete).delete()
        
        # Eliminar el paquete
        paquete.delete()
        
        return Response({"message": "Paquete eliminado con éxito"}, status=status.HTTP_200_OK)
    except Exception as e:
        # Si ocurre un error, se hará rollback automáticamente
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   