from decimal import Decimal
from django.db import models

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)  # identificador único
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    ubicacion = models.CharField(max_length=100, blank=True, null=True)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} ({self.sku})"