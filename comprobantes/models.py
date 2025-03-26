from django.db import models

class Comprobante(models.Model):
    tipo_comprobante = models.CharField(max_length=50)
    numero_comprobante = models.CharField(max_length=50, unique=True)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField(null=True, blank=True)
    cuit_emisor = models.CharField(max_length=11)
    nombre_emisor = models.CharField(max_length=255)
    cuit_receptor = models.CharField(max_length=11, null=True, blank=True)
    nombre_receptor = models.CharField(max_length=255, null=True, blank=True)
    condicion_iva = models.CharField(max_length=50)
    condicion_venta = models.CharField(max_length=50)
    total = models.DecimalField(max_digits=15, decimal_places=2)
    moneda = models.CharField(max_length=10, default='ARS')
    cae = models.CharField(max_length=14, null=True, blank=True)
    fecha_vencimiento_cae = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.tipo_comprobante} {self.numero_comprobante}"

class DetalleComprobante(models.Model):
    comprobante = models.ForeignKey(Comprobante, on_delete=models.CASCADE, related_name="detalles")
    codigo_producto = models.CharField(max_length=50, null=True, blank=True)
    descripcion = models.TextField()
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=15, decimal_places=2)
    iva = models.DecimalField(max_digits=5, decimal_places=2, default=21.00)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.descripcion} - {self.cantidad}"