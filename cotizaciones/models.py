from django.db import models
from clientes.models import Cliente
from productos.models import Producto
from paquetes.models import Paquete
from clientes.models import Cliente
from catalogos.models import Catalogo
from django.utils.timezone import now 
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth.models import User 

class Cotizacion(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True) 
    cliente = models.ForeignKey(
        Cliente, 
        related_name='cotizaciones', 
        on_delete=models.CASCADE, 
        db_column='clientes_id'
    )    
    iva = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tipo_descuento = models.PositiveSmallIntegerField(null=True, blank=True)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estado = models.PositiveSmallIntegerField(default=1, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Agrega el campo user como ForeignKey al modelo User de Django
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cotizaciones',
        db_column='user_id'
    )

    def __str__(self):
        # return self.cotizaciones
        return f'Cotización {self.id} - Cliente: {self.cliente.nombre} - Total: {self.total}'  

    def save(self, *args, **kwargs):
        # Si el IVA es nulo, lo trata como 0
        iva_porcentaje = self.iva or 0
        # Calcula el total considerando el IVA
        total_calculado = self.subtotal + (self.subtotal * iva_porcentaje / 100)
        # Redondea el total a 2 decimales
        self.total = Decimal(total_calculado).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        # Si el estado es nulo, lo establece a 1
        if self.estado is None:
            self.estado = 1
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'cotizaciones'
        managed = True
        verbose_name = 'cotizaciones'
        verbose_name_plural = 'cotizaciones'

class CotizacionDetalle(models.Model):
    cantidad = models.CharField(max_length=45, null=True, blank=True)
    duracion_horas = models.CharField(max_length=45, null=True, blank=True)    
    cotizacion = models.ForeignKey(
        Cotizacion, 
        related_name='detalles', 
        on_delete=models.CASCADE, 
        db_column='cotizaciones_id'        
    )    
    producto = models.ForeignKey(
        Producto, 
        related_name='productos', 
        on_delete=models.CASCADE, 
        db_column='producto_id',
        null=True,
        blank=True
    )    
    paquete = models.ForeignKey(
        Paquete, 
        related_name='paquetes', 
        on_delete=models.CASCADE, 
        db_column='paquetes_id',
        null=True,
        blank=True
    )
    tipo_item = models.PositiveSmallIntegerField(null=True, blank=True)
    iva = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.cotizacion_detalle

    class Meta:
        db_table = 'cotizacion_detalle'
        managed = True
        verbose_name = 'cotizacion_detalle'
        verbose_name_plural = 'cotizacion_detalle'