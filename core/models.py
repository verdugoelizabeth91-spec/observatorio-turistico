from django.db import models

# Create your models here.
from django.db import models

class RegistroObservatorio(models.Model):
    OPCIONES_TIPO = [
        ('social', 'Social / Demográfico'),
        ('economico', 'Económico / Comercial'),
        ('ambiental', 'Ambiental / Agrícola'),
        ('seguridad', 'Seguridad / Infraestructura'),
    ]

    titulo = models.CharField(max_length=150)
    tipo = models.CharField(max_length=20, choices=OPCIONES_TIPO)
    valor = models.FloatField()
    fecha = models.DateField()
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.fecha} - {self.titulo} ({self.tipo}) - {self.valor}"