from rest_framework import serializers
from . import models
from .models import Paquete, PaqueteDetalle
from productos.models import Producto

class PaqueteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paquete
        fields = '__all__'

class PaqueteDetalleSerializer(serializers.ModelSerializer):
    paquete = serializers.PrimaryKeyRelatedField(queryset=Paquete.objects.all())
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())

    class Meta:
        model = PaqueteDetalle
        fields = '__all__'