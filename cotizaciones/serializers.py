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
    user = serializers.SerializerMethodField()
    estado_info = serializers.SerializerMethodField()
    evento = serializers.SerializerMethodField()

    # NUEVO: Método para inicializar con datos precargados
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si hay muchas instancias, precargar catálogos UNA SOLA VEZ
        if hasattr(self, 'many') and self.many and self.instance is not None:
            # Cachear catálogos en el contexto para evitar consultas repetidas
            if 'catalogos_grupo3' not in self.context:
                self.context['catalogos_grupo3'] = {
                    c.codigo: {'item': c.item, 'color': c.color}
                    for c in Catalogo.objects.filter(grupo=3)
                }
            if 'catalogos_grupo4' not in self.context:
                self.context['catalogos_grupo4'] = {
                    c.codigo: {'item': c.item}
                    for c in Catalogo.objects.filter(grupo=4)
                }

    def get_user(self, obj):
        if obj.user:
            return obj.user.first_name if obj.user.first_name else obj.user.username
        return None    

    def get_estado_info(self, obj):
        """Versión optimizada que usa el caché del contexto"""
        # Primero intentar del contexto (más rápido)
        catalogos = self.context.get('catalogos_grupo3')
        if catalogos is not None:
            return catalogos.get(obj.estado)
        
        # Fallback al método original (por si acaso)
        estado_catalogo = Catalogo.objects.filter(grupo=3, codigo=obj.estado).first()
        if estado_catalogo:
            return {
                'item': estado_catalogo.item,
                'color': estado_catalogo.color
            }
        return None

    def get_evento(self, obj):
        """Versión optimizada que usa el caché del contexto"""
        # Primero intentar del contexto (más rápido)
        catalogos = self.context.get('catalogos_grupo4')
        if catalogos is not None:
            evento = catalogos.get(obj.tipo_evento)
            return evento if evento else None
        
        # Fallback al método original
        tipo_evento = Catalogo.objects.filter(grupo=4, codigo=obj.tipo_evento).first()
        if tipo_evento:
            return {
                'item': tipo_evento.item
            }
        return None

    # El resto del serializador sigue IGUAL...
    class Meta:
        db_table = 'cotizaciones'
        model = Cotizacion
        fields = '__all__'       


class CotizacionFastListSerializer(serializers.ModelSerializer):
    """Serializador RÁPIDO para listas - datos mínimos"""
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_identificacion = serializers.CharField(source='cliente.identificacion', read_only=True)
    usuario = serializers.CharField(source='user.first_name', read_only=True, default='')
    total_detalles = serializers.SerializerMethodField()
    estado_texto = serializers.SerializerMethodField()
    tipo_evento_texto = serializers.SerializerMethodField()
    
    def get_total_detalles(self, obj):
        return obj.detalles.count()
    
    def get_estado_texto(self, obj):
        # Cachear en memoria (evita consultas)
        if not hasattr(self, '_estados_cache'):
            self._estados_cache = {
                c.codigo: c.item 
                for c in Catalogo.objects.filter(grupo=3)
            }
        return self._estados_cache.get(obj.estado, '')
    
    def get_tipo_evento_texto(self, obj):
        if not hasattr(self, '_eventos_cache'):
            self._eventos_cache = {
                c.codigo: c.item 
                for c in Catalogo.objects.filter(grupo=4)
            }
        return self._eventos_cache.get(obj.tipo_evento, '')
    
    class Meta:
        model = Cotizacion
        fields = [
            'id', 'fecha_creacion', 'codigo',
            'cliente_nombre', 'cliente_identificacion',
            'usuario', 'total', 'estado_texto', 
            'tipo_evento_texto', 'total_detalles'
        ]        