from django.contrib import admin
from .models import RegistroObservatorio

@admin.register(RegistroObservatorio)
class RegistroObservatorioAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'titulo', 'tipo', 'valor')
    list_filter = ('tipo', 'fecha')
    search_fields = ('titulo', 'observaciones')