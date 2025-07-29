from rest_framework import serializers
from . import models
from .models import Producto
from catalogos.models import Catalogo
from categoria_producto.serializers import CategoriaProductoSerializer
# from inventario.serializers import InventarioSerializer

class ProductoSerializer(serializers.ModelSerializer):    
    user = serializers.SerializerMethodField()
    estado_info = serializers.SerializerMethodField()
    tipo_costo_info = serializers.SerializerMethodField()
    categoria_info = CategoriaProductoSerializer(source='categoria_producto_id', read_only=True)
    # inventarios = InventarioSerializer(many=True, read_only=True) 

    class Meta:
        model = Producto
        fields = '__all__'
    
    def get_user(self, obj):
        """
        Devuelve el first_name del usuario si existe, 
        de lo contrario devuelve el username.
        """
        if obj.user:
            return obj.user.first_name if obj.user.first_name else None
        return None    

    def get_estado_info(self, obj):
        """Obtiene el estado desde la tabla Catalogo filtrando por grupo=3."""        
        estado_catalogo = Catalogo.objects.filter(grupo=2, codigo=obj.estado).first()
        if estado_catalogo:
            return {
                'item': estado_catalogo.item,
                'color': estado_catalogo.color
            }
        return None  # Si no encuentra el estado     

    def get_tipo_costo_info(self, obj):
        """Obtiene el estado desde la tabla Catalogo filtrando por grupo=3."""        
        estado_catalogo = Catalogo.objects.filter(grupo=1, codigo=obj.tipo_costo).first()
        if estado_catalogo:
            return {
                'item': estado_catalogo.item,
                'color': estado_catalogo.color
            }
        return None  # Si no encuentra el estado                

    def create(self, validated_data):
        # Asigna el usuario logueado al campo 'user'
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)      

    def update(self, instance, validated_data):
        # Asigna el usuario logueado al campo 'user' al actualizar un producto
        validated_data['user'] = self.context['request'].user
        return super().update(instance, validated_data)

    def get_inventario_updated_at(self, obj):
        return obj.inventario_updated_at.strftime('%Y-%m-%d %H:%M:%S') if obj.inventario_updated_at else None        
