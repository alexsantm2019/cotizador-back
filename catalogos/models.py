from django.db import models

# Create your models here.

class Catalogo(models.Model):
    grupo = models.IntegerField(null=True, blank=True)
    codigo = models.IntegerField(null=True, blank=True)
    item = models.CharField(max_length=45, null=True, blank=True)
    detalle = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=20, null=True, blank=True)
    
    class Meta:
        db_table = 'catalogo'
        managed = True
        verbose_name = 'catalogo'
        verbose_name_plural = 'catalogo'

    def __str__(self):
        return f"{self.item} ({self.codigo})"
