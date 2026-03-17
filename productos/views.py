from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Producto
from .serializers import ProductoSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
import datetime
import json
from rest_framework.parsers import JSONParser
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

@api_view(['GET'])
def get_productos(request):
    productos = Producto.objects.filter(deleted_at__isnull=True)
    serializer = ProductoSerializer(productos, many=True, context={'request': request})  # Agregar contexto
    return JsonResponse(serializer.data, safe=False) 

@api_view(['GET'])
def get_productos_optimizado(request):
    """
    Endpoint optimizado para obtener productos con paginación y búsqueda
    """
    # Parámetros de paginación
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    search = request.GET.get('search', '')  # 👈 NUEVO: parámetro de búsqueda
    
    # Consulta base
    productos_query = Producto.objects.filter(
        deleted_at__isnull=True
    ).select_related(
        'user', 'categoria_producto_id'
    )
    
    # 👇 APLICAR FILTRO DE BÚSQUEDA SI EXISTE
    if search:
        productos_query = productos_query.filter(
            Q(producto__icontains=search) |  # Buscar en nombre
            Q(descripcion__icontains=search) |  # Buscar en descripción
            Q(ubicacion__icontains=search)  # Buscar en ubicación
        )
    
    # Ordenar
    productos_query = productos_query.order_by('-id')
    
    # Paginación
    paginator = Paginator(productos_query, page_size)
    
    try:
        productos_page = paginator.page(page)
    except:
        productos_page = paginator.page(1)
    
    # Cachear catálogos (igual que antes)
    from catalogos.models import Catalogo
    catalogos = Catalogo.objects.filter(grupo__in=[1, 2])
    
    catalogos_grupo1 = {}
    catalogos_grupo2 = {}
    
    for cat in catalogos:
        if cat.grupo == 1:
            catalogos_grupo1[cat.codigo] = {'item': cat.item, 'color': cat.color}
        elif cat.grupo == 2:
            catalogos_grupo2[cat.codigo] = {'item': cat.item, 'color': cat.color}
    
    context = {
        'request': request,
        'catalogos_grupo1': catalogos_grupo1,
        'catalogos_grupo2': catalogos_grupo2
    }
    
    serializer = ProductoSerializer(productos_page, many=True, context=context)
    
    return Response({
        'data': serializer.data,
        'pagination': {
            'total': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'has_next': productos_page.has_next(),
            'has_previous': productos_page.has_previous()
        },
        'search': search  
    })

@api_view(['GET'])
def get_productos_inventario(request):
    productos = Producto.objects.filter(tipo_costo=1,deleted_at__isnull=True)
    serializer = ProductoSerializer(productos, many=True, context={'request': request})  # Agregar contexto
    return JsonResponse(serializer.data, safe=False) 

@api_view(['POST'])
def create_producto(request):	
    if request.method == 'POST':
        # serializer = ProductoSerializer(data=request.data)
        serializer = ProductoSerializer(data=request.data, context={'request': request})    # Para agregar user_id
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

@api_view(['PUT'])
def update_producto(request, producto_id):
    try:
        producto = Producto.objects.get(pk=producto_id)
    except Producto.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        # serializer = ProductoSerializer(producto, data=request.data, context={'action': 'update'})
        serializer = ProductoSerializer(producto, data=request.data, context={'request': request}, partial=(request.method == 'PATCH')) # Para agregar user_id
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_inventario(request, producto_id):
    try:
        producto = Producto.objects.get(id=producto_id)
        nueva_cantidad = request.data.get("cantidad")

        if nueva_cantidad is None:
            return Response({"error": "El campo 'cantidad' es requerido."}, status=status.HTTP_400_BAD_REQUEST)

        producto.cantidad = nueva_cantidad
        now = datetime.datetime.now()  # Mismo método que delete_producto
        producto.inventario_updated_at = now
        producto.save()

        return Response({"mensaje": "Inventario actualizado correctamente"}, status=status.HTTP_200_OK)

    except Producto.DoesNotExist:
        return Response({"error": "Producto no encontrado"}, status=status.HTTP_404_NOT_FOUND)       

@api_view(['DELETE'])
def delete_producto(request, producto_id):
    try:
        producto = Producto.objects.get(pk=producto_id)
    except Producto.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Cambiar el estado del producto a eliminado
    now = datetime.datetime.now()
    producto.deleted_at  = now
    producto.save()
    return Response(status=status.HTTP_204_NO_CONTENT) 
 