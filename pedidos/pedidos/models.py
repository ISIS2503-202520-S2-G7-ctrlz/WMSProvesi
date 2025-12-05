from django.db import models

# Create your models here.
class Pedido(models.Model):
    ESTADOS = [
        ("transito", "Transito"),
        ("alistamiento", "Alistamiento"),
        ("por_verificar", "Por Verificar"),
        ("rechazado_x_verificar", "Rechazado x Verificar"),
        ("verificado", "Verificado"),
        ("empacado_x_despacho", "Empacado x Despacho"),
        ("despachado", "Despachado"),
        ("despachado_x_facturacion", "Despachado x Facturacion"),
        ("entregado", "Entregado"),
        ("devuelto", "Devuelto"),
        ("produccion", "Produccion"),
        ("bordado", "Bordado"),
        ("dropshipping", "Dropshipping"),
        ("compra", "Compra"),
        ("anulado", "Anulado"),
    ]

    codigo = models.CharField(max_length=50, unique=True)
    cliente = models.CharField(max_length=100)
    estado = models.CharField(max_length=40, choices=ESTADOS, default="transito")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    detalles = models.TextField(blank=True, null=True)
    productos = models.JSONField() 


    def __str__(self):
        return f"Pedido {self.codigo} - {self.estado}"
