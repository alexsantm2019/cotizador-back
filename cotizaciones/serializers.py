from rest_framework import serializers
# from . import models
from .models import Cotizacion, CotizacionDetalle
from productos.serializers import ProductoSerializer
from paquetes.serializers import PaqueteSerializer
from clientes.serializers import ClienteSerializer
from productos.models import Producto
from paquetes.models import Paquete
from clientes.models import Cliente
from catalogos.models import Catalogo

class CotizacionDetalleSerializer(serializers.ModelSerializer):
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all(), required=False, allow_null=True)
    paquete = serializers.PrimaryKeyRelatedField(queryset=Paquete.objects.all(), required=False, allow_null=True)

    info_producto = ProductoSerializer(source='producto', read_only=True)
    info_paquete = PaqueteSerializer(source='paquete', read_only=True)    

    class Meta:
        db_table = 'cotizacion_detalle'
        model = CotizacionDetalle
        fields = '__all__'

    def validate(self, data):
        producto = data.get('producto')
        paquete = data.get('paquete')
        
        # Validar que al menos uno de los dos campos no sea nulo, pero no ambos
        if producto is None and paquete is None:
            raise serializers.ValidationError("Debe especificar un 'producto' o un 'paquete'.")
        if producto is not None and paquete is not None:
            raise serializers.ValidationError("No puede especificar tanto 'producto' como 'paquete' al mismo tiempo.")
        
        return data     

class CotizacionSerializer(serializers.ModelSerializer):        
    info_cliente = ClienteSerializer(source='cliente', read_only=True)
    detalles = CotizacionDetalleSerializer(many=True, read_only=True)
    user = serializers.SerializerMethodField()  # Usamos un método para obtener el nombre del usuario
    estado_info = serializers.SerializerMethodField()  # Agregamos un método para obtener la información del estado

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
        estado_catalogo = Catalogo.objects.filter(grupo=3, codigo=obj.estado).first()
        if estado_catalogo:
            return {
                'item': estado_catalogo.item,
                'color': estado_catalogo.color
            }
        return None  # Si no encuentra el estado          

    class Meta:
        db_table = 'cotizaciones'
        model = Cotizacion
        fields = '__all__'
        # extra_fields = ['estado_info']

    def create(self, validated_data):
        # Asigna el usuario logueado al campo 'user'
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)     

    def update(self, instance, validated_data):
        # Asigna el usuario logueado al campo 'user' al actualizar un producto
        validated_data['user'] = self.context['request'].user
        return super().update(instance, validated_data)        