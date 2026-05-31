from django.contrib import admin
from .models import RegistroTurista

@admin.register(RegistroTurista)
class RegistroTuristaAdmin(admin.ModelAdmin):
    list_display = ('fecha_registro', 'num_personas', 'procedencia', 'lugar_especifico', 'motivo_viaje')
    list_filter = ('procedencia', 'motivo_viaje', 'fecha_registro')
    search_fields = ('lugar_especifico',)