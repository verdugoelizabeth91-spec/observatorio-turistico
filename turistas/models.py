from django.db import models
from django.utils import timezone


class RegistroTurista(models.Model):
    TIPO_ORIGEN = [
        ('nacional', 'Nacional'),
        ('extranjero', 'Extranjero'),
    ]

    TIPO_VISITA = [
        ('individual', 'Visitantes'),
        ('grupo', 'Grupo'),
    ]

    MOTIVOS_VIAJE = [
        ('hospedaje',      'Hospedaje'),
        ('gastronomia',    'Gastronomía'),
        ('compras',        'Compras'),
        ('negocios',       'Negocios'),
        ('turismo_rural',  'Turismo Rural'),
        ('rutas_senderos', 'Rutas/Senderos'),
        ('par_naturales',  'Par. Naturales'),
        ('religioso',      'Religioso/Peregrinación'),
        ('a_culturales',   'A. Culturales'),
        ('fiestas',        'Fiestas'),
        ('artesania',      'Artesanía'),
        ('ocio',           'Ocio'),
        ('a_deportivas',   'A. Deportivas'),
        ('transportes',    'Transportes'),
        ('biblian',        'Biblián'),
        ('canar',          'Cañar'),
        ('el_tambo',       'El Tambo'),
        ('suscal',         'Suscal'),
        ('ingapirca',      'Ingapirca'),
        ('banos_inca',     'Baños del Inca'),
        ('virgen_rocio',   'Virgen del Rocío'),
        ('otros',          'Otros'),
    ]

    RANGO_EDAD = [
        ('jovenes',         'Jóvenes (16 a 25 años)'),
        ('adultos',         'Adultos (26 a 50 años)'),
        ('adultos_mayores', '51 años en adelante'),
    ]

    TRANSPORTE = [
        ('vehiculo_propio',      'Vehículo Propio'),
        ('bus_publico',          'Bus Público'),
        ('transporte_turistico', 'Transporte Turístico'),
    ]

    COMPOSICION = [
        ('pareja',  'En Pareja'),
        ('familia', 'En Familia'),
        ('amigos',  'Con Amigos'),
        ('trabajo', 'Actividades de Trabajo'),
    ]

    tipo_visita       = models.CharField(max_length=20, choices=TIPO_VISITA, default='individual')
    num_personas      = models.IntegerField(default=1)
    procedencia       = models.CharField(max_length=20, choices=TIPO_ORIGEN, default='nacional')
    lugar_especifico  = models.CharField(max_length=100)
    lugar_detalle     = models.CharField(max_length=100, blank=True, null=True)
    rango_edad        = models.CharField(max_length=20, choices=RANGO_EDAD, blank=True, null=True)
    medio_transporte  = models.CharField(max_length=30, choices=TRANSPORTE, blank=True, null=True)
    composicion_grupo = models.CharField(max_length=20, choices=COMPOSICION, blank=True, null=True)
    estadia_dias      = models.IntegerField(default=0)
    estadia_noches    = models.IntegerField(default=0)
    motivo_viaje      = models.CharField(max_length=50, choices=MOTIVOS_VIAJE, default='otros')
    motivo_otro       = models.CharField(max_length=200, blank=True, null=True)
    fecha_registro    = models.DateTimeField(default=timezone.now, blank=True)

    def __str__(self):
        return f"{self.lugar_especifico} - {self.num_personas} personas"