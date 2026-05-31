from django.db import models

class RegistroTurista(models.Model):
    TIPO_ORIGEN = [
        ('nacional', 'Nacional'),
        ('extranjero', 'Extranjero'),
    ]
    
    MOTIVOS_VIAJE = [
        ('turismo_rural', 'Turismo Rural'),
        ('visita_familiar', 'Visita Familiar'),
        ('paso', 'Paso'),
    ]

    num_personas = models.IntegerField(default=1)
    procedencia = models.CharField(max_length=20, choices=TIPO_ORIGEN, default='nacional')
    lugar_especifico = models.CharField(max_length=100)
    motivo_viaje = models.CharField(max_length=50, choices=MOTIVOS_VIAJE, default='paso')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lugar_especifico} - {self.num_personas} personas"