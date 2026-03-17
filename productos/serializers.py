from rest_framework import serializers
from .models import Producto

class ProductoSerializer(serializers.ModelSerializer):    
    user = serializers.SerializerMethodField()
    estado_info = serializers.SerializerMethodField()
    tipo_costo_info = serializers.SerializerMethodField()
    categoria_info = serializers.SerializerMethodField()  # Cambiar a MethodField para más control
    # inventarios = serializers.SerializerMethodField()  # Si necesitas inventarios

    class Meta:
        model = Producto
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Cachear catálogos del contexto si existen
        self.catalogos_grupo1 = self.context.get('catalogos_grupo1', {})
        self.catalogos_grupo2 = self.context.get('catalogos_grupo2', {})
        
        # Opcional: Cachear categorías si son muchas
        if not hasattr(self, '_categorias_cache'):
            from categoria_producto.models import CategoriaProducto
            self._categorias_cache = {
                c.id: {'id': c.id, 'nombre': c.categoria}
                for c in CategoriaProducto.objects.all()
            }

    def get_user(self, obj):
        """Devuelve el nombre del usuario (sin consulta adicional)"""
        if obj.user:
            return obj.user.first_name or obj.user.username
        return None

    def get_estado_info(self, obj):
        """Usa el catálogo cacheado en lugar de consultar BD"""
        return self.catalogos_grupo2.get(obj.estado)

    def get_tipo_costo_info(self, obj):
        """Usa el catálogo cacheado en lugar de consultar BD"""
        return self.catalogos_grupo1.get(obj.tipo_costo)

    def get_categoria_info(self, obj):
        """Usa el caché de categorías si existe, o devuelve datos básicos"""
        if obj.categoria_producto_id:
            # Si tenemos caché, úsalo
            if hasattr(self, '_categorias_cache'):
                return self._categorias_cache.get(obj.categoria_producto_id.id)
            
            # Si no hay caché, devuelve datos básicos del objeto
            return {
                'id': obj.categoria_producto_id.id,
                'nombre': obj.categoria_producto_id.nombre
            }
        return None

    # Si necesitas inventarios, optimízalo también
    # def get_inventarios(self, obj):
    #     # Usar prefetch_related ya cargó los inventarios
    #     if hasattr(obj, 'inventarios') and obj.inventarios.all():
    #         return [{
    #             'id': inv.id,
    #             'cantidad': inv.cantidad,
    #             'ubicacion': inv.ubicacion
    #         } for inv in obj.inventarios.all()]
    #     return []

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().update(instance, validated_data)