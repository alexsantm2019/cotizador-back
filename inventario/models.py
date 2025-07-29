from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from productos.models import Producto  # Asegúrate de importar correctamente el modelo Producto

class Inventario(models.Model):
    id = models.AutoField(primary_key=True)  # Define la PK como INT explícitamente
    created_at = models.DateTimeField(auto_now_add=True)  # Se almacena la fecha de creación    
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    producto = models.ForeignKey(
        Producto,  # Referencia al modelo Producto
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='inventarios',
        db_column='producto_id'
    )
    cantidad = models.IntegerField(default=0)  # Se registra la cantidad del producto en inventario
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='inventarios',
        db_column='user_id'
    )
    
    def __str__(self):
        return f"{self.producto.producto} - {self.cantidad}"

    class Meta:
        db_table = 'inventario'