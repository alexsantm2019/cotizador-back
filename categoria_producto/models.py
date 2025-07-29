from django.db import models

# Create your models here.

class CategoriaProducto(models.Model):
    categoria = models.CharField(max_length=45, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.categoria  
    
    class Meta:
        db_table = 'categoria_producto'
        managed = True
        verbose_name = 'categoria_producto'
        verbose_name_plural = 'categoria_producto'