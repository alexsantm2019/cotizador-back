from django.db import models
from categoria_producto.models import CategoriaProducto
from catalogos.models import Catalogo
# from .models import Producto, Catalogo, CategoriaProducto
from django.contrib.auth.models import User 
from catalogos.serializers import CatalogoSerializer

# Create your models here.

class Producto(models.Model):
    id = models.AutoField(primary_key=True) 
    producto = models.CharField(max_length=100, null=True, blank=True)
    # descripcion = models.TextField(max_length=200, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    tipo_costo = models.PositiveSmallIntegerField(null=True, blank=True) # Mantenerlo como IntegerField ( si no es FK)
    costo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estado = models.IntegerField(null=True, blank=True) # Mantenerlo como IntegerField ( si no es FK)
    ubicacion = models.CharField(max_length=45, null=True, blank=True)
    cantidad = models.IntegerField(null=True, blank=True)
    inventario_updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    categoria_producto_id = models.ForeignKey(
        'categoria_producto.CategoriaProducto',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='producto',
        db_column='categoria_producto_id'
    )

    # Agrega el campo user como ForeignKey al modelo User de Django
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user',
        db_column='user_id'
    )

    # Si no existe relación en la base de datos, hay que comentar (si no existe relacion en bdd)
    # estado = models.ForeignKey(
    #     Catalogo,
    #     on_delete=models.CASCADE,
    #     null=True,
    #     blank=True,
    #     related_name='productos',
    #     db_column='estado'
    # )

    def __str__(self):
        return self.producto  
    
    class Meta:
        db_table = 'productos'
        managed = True
        verbose_name = 'productos'
        verbose_name_plural = 'productos'
   
    def __str__(self):
        return f"{self.productos}"