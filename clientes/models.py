from django.db import models

# Create your models here.

class Cliente(models.Model):
    nombre = models.CharField(max_length=100, null=True, blank=True)
    identificacion = models.CharField(max_length=13, null=True, blank=True)
    correo = models.EmailField(max_length=45, null=True, blank=True)
    telefono = models.CharField(max_length=10, null=True, blank=True)
    direccion = models.CharField(max_length=100, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.cliente  
    
    class Meta:
        db_table = 'clientes'
        managed = True
        verbose_name = 'clientes'
        verbose_name_plural = 'clientes'