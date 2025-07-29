from django.db import models
from productos.models import Producto
from categoria_producto.models import CategoriaProducto

# Create your models here.

class Paquete(models.Model):
    nombre_paquete = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.TextField(max_length=200, null=True, blank=True)
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estado = models.PositiveSmallIntegerField(null=True, blank=True)

    categoria_producto_id = models.ForeignKey(
        'categoria_producto.CategoriaProducto',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='paquetes',
        db_column='categoria_producto_id'
    )

    def __str__(self):
        return self.nombre_paquete

    class Meta:
        db_table = 'paquetes'
        managed = True
        verbose_name = 'paquetes'
        verbose_name_plural = 'paquetes'

class PaqueteDetalle(models.Model):
    paquete = models.ForeignKey(
        Paquete, 
        related_name='detalles', 
        on_delete=models.CASCADE, 
        db_column='paquetes_id'  # Nombre explícito de la columna
    )
    producto = models.ForeignKey(
        Producto, 
        related_name='detalles_paquete', 
        on_delete=models.CASCADE, 
        db_column='productos_id'  # Nombre explícito de la columna
    )
    cantidad = models.CharField(max_length=45, null=True, blank=True)
    duracion_horas = models.CharField(max_length=45, null=True, blank=True)
    costo_producto = models.DecimalField(max_digits=10, decimal_places=2)
    # paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.paquete.nombre_paquete} - {self.producto.producto}"

    class Meta:
        db_table = 'paquete_detalle'
        managed = True
        verbose_name = 'paquete_detalle'
        verbose_name_plural = 'paquete_detalle'
    