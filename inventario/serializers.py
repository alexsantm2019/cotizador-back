from rest_framework import serializers
from .models import Inventario
from productos.serializers import ProductoSerializer

class InventarioSerializer(serializers.ModelSerializer):
    producto_info = ProductoSerializer(source='producto', read_only=True)
    user = serializers.SerializerMethodField()
    # producto = ProductoSerializer(read_only=True)

    class Meta:
        model = Inventario
        fields = '__all__'

    def get_producto_info(self, obj):
        # Realizamos el import dentro de la función para evitar circular import
        from productos.serializers import ProductoSerializer
        # Serializamos el producto relacionado
        return ProductoSerializer(obj.producto).data        

    def get_user(self, obj):
        if obj.user:
            return obj.user.first_name if obj.user.first_name else None
        return None