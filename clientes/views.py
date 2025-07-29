from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Cliente
from .serializers import ClienteSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
import datetime
import json
from rest_framework.parsers import JSONParser

@api_view(['GET'])
def get_clientes(request):   
    clientes = Cliente.objects.filter(deleted_at__isnull=True)
    serializer = ClienteSerializer(clientes, many=True)
    return JsonResponse(serializer.data, safe=False) 

@api_view(['POST'])
def create_cliente(request):	
    if request.method == 'POST':
        serializer = ClienteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

@api_view(['PUT'])
def update_cliente(request, cliente_id):
    try:
        cliente = Cliente.objects.get(pk=cliente_id)
    except Cliente.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = ClienteSerializer(cliente, data=request.data, context={'action': 'update'})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_cliente(request, cliente_id):
    try:
        cliente = Cliente.objects.get(pk=cliente_id)
    except Cliente.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Cambiar el estado del producto a eliminado
    now = datetime.datetime.now()
    cliente.deleted_at  = now
    cliente.save()
    return Response(status=status.HTTP_204_NO_CONTENT) 
 