from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth
from django.utils import timezone
from .models import RegistroTurista
from datetime import date, datetime
import json

MOTIVOS_LABELS = {
    'hospedaje':      'Hospedaje',
    'gastronomia':    'Gastronomía',
    'compras':        'Compras',
    'negocios':       'Negocios',
    'turismo_rural':  'Turismo Rural',
    'rutas_senderos': 'Rutas/Senderos',
    'par_naturales':  'Par. Naturales',
    'religioso':      'Religioso/Peregrinación',
    'a_culturales':   'A. Culturales',
    'fiestas':        'Fiestas',
    'artesania':      'Artesanía',
    'ocio':           'Ocio',
    'a_deportivas':   'A. Deportivas',
    'transportes':    'Transportes',
    'biblian':        'Biblián',
    'canar':          'Cañar',
    'el_tambo':       'El Tambo',
    'suscal':         'Suscal',
    'ingapirca':      'Ingapirca',
    'banos_inca':     'Baños del Inca',
    'virgen_rocio':   'Virgen del Rocío',
    'otros':          'Otros',
}

MESES = ['enero','febrero','marzo','abril','mayo','junio',
         'julio','agosto','septiembre','octubre','noviembre','diciembre']

LUGARES_NACIONALES = [
    'canar','el_tambo','suscal','biblian','cuenca','quito',
    'guayaquil','zona_sierra','zona_costa','zona_oriente','galapagos','manta','riobamba'
]

LUGARES_LABELS = {
    'canar':           'Cañar',
    'el_tambo':        'El Tambo',
    'suscal':          'Suscal',
    'biblian':         'Biblián',
    'cuenca':          'Cuenca',
    'quito':           'Quito',
    'guayaquil':       'Guayaquil',
    'manta':           'Manta',
    'riobamba':        'Riobamba',
    'zona_sierra':     'Zona Sierra',
    'zona_costa':      'Zona Costa',
    'zona_oriente':    'Zona Oriente',
    'galapagos':       'Galápagos',
    'estados_unidos':  'Estados Unidos',
    'canada':          'Canadá',
    'francia':         'Francia',
    'peru':            'Perú',
    'colombia':        'Colombia',
    'america_sur':     'América del Sur',
    'europa':          'Europa',
    'africa':          'África',
    'asia':            'Asia',
    'otro_extranjero': 'Otro',
}


@login_required
def formulario_registro(request, id_registro=None):
    registro = None
    if id_registro:
        registro = get_object_or_404(RegistroTurista, id=id_registro)

    if request.method == 'POST':
        tipo_visita       = request.POST.get('tipo_visita')
        num_personas      = request.POST.get('num_personas')
        procedencia       = request.POST.get('procedencia')
        lugar_especifico  = request.POST.get('lugar_especifico')
        rango_edad        = request.POST.get('rango_edad')
        medio_transporte  = request.POST.get('medio_transporte')
        composicion_grupo = request.POST.get('composicion_grupo')
        estadia_dias      = request.POST.get('estadia_dias') or 0
        estadia_noches    = request.POST.get('estadia_noches') or 0
        motivo_viaje      = request.POST.get('motivo_viaje')
        motivo_otro       = request.POST.get('motivo_otro', '').strip()

        if registro:
            registro.tipo_visita       = tipo_visita
            registro.num_personas      = num_personas
            registro.procedencia       = procedencia
            registro.lugar_especifico  = lugar_especifico
            registro.rango_edad        = rango_edad
            registro.medio_transporte  = medio_transporte
            registro.composicion_grupo = composicion_grupo
            registro.estadia_dias      = estadia_dias
            registro.estadia_noches    = estadia_noches
            registro.motivo_viaje      = motivo_viaje
            registro.motivo_otro       = motivo_otro if motivo_viaje == 'otros' else ''
            registro.save()
            messages.success(request, '¡Registro editado y actualizado correctamente!')
        else:
            RegistroTurista.objects.create(
                tipo_visita       = tipo_visita,
                num_personas      = num_personas,
                procedencia       = procedencia,
                lugar_especifico  = lugar_especifico,
                rango_edad        = rango_edad,
                medio_transporte  = medio_transporte,
                composicion_grupo = composicion_grupo,
                estadia_dias      = estadia_dias,
                estadia_noches    = estadia_noches,
                motivo_viaje      = motivo_viaje,
                motivo_otro       = motivo_otro if motivo_viaje == 'otros' else '',
                fecha_registro    = timezone.now(),
            )
            messages.success(request, '¡Registro guardado exitosamente!')

        return redirect('formulario_registro')

    registros = RegistroTurista.objects.filter(
        fecha_registro__date=date.today()
    ).order_by('-id')

    return render(request, 'turistas/formulario.html', {
        'registro':      registro,
        'registros':     registros,
        'motivos_lista': MOTIVOS_LABELS.items(),
    })


@login_required
def eliminar_registro(request, id_registro):
    registro = get_object_or_404(RegistroTurista, id=id_registro)
    registro.delete()
    messages.success(request, '¡Registro eliminado correctamente!')
    return redirect('formulario_registro')


@login_required
def guardar_datos_personalizados(request):
    if request.method == 'POST':
        modo     = request.POST.get('modo')
        mes      = int(request.POST.get('mes'))
        anio_raw = request.POST.get('anio')
        anio = int(anio_raw) if anio_raw else 2026

        if modo == 'dia':
            dia   = int(request.POST.get('dia'))
            fecha = datetime(anio, mes, dia, 12, 0, 0)

            procedencia      = request.POST.get('procedencia')
            lugar_especifico = request.POST.get('lugar_especifico')

            if lugar_especifico in ('zona_costa', 'zona_sierra', 'zona_oriente'):
                lugar_especifico = request.POST.get('modal_zona_detalle', lugar_especifico)
            elif lugar_especifico == 'otro_extranjero':
                lugar_especifico = request.POST.get('modal_extranjero_detalle', lugar_especifico)

            tipo_visita       = request.POST.get('tipo_visita', 'individual')
            num_personas      = int(request.POST.get('num_personas', 1))
            rango_edad        = request.POST.get('rango_edad', '')
            medio_transporte  = request.POST.get('medio_transporte', '')
            composicion_grupo = request.POST.get('composicion_grupo', '')
            estadia_dias      = int(request.POST.get('estadia_dias') or 0)
            estadia_noches    = int(request.POST.get('estadia_noches') or 0)
            motivo_viaje      = request.POST.get('motivo_viaje', 'otros')
            motivo_otro       = request.POST.get('motivo_otro', '').strip()

            RegistroTurista.objects.create(
                tipo_visita       = tipo_visita,
                num_personas      = num_personas,
                procedencia       = procedencia,
                lugar_especifico  = lugar_especifico,
                rango_edad        = rango_edad,
                medio_transporte  = medio_transporte,
                composicion_grupo = composicion_grupo,
                estadia_dias      = estadia_dias,
                estadia_noches    = estadia_noches,
                motivo_viaje      = motivo_viaje,
                motivo_otro       = motivo_otro if motivo_viaje == 'otros' else '',
                fecha_registro    = fecha,
            )
            messages.success(request, f'✅ Registro del {dia}/{mes}/{anio} guardado correctamente.')

        elif modo == 'mes':
            guardados = 0
            i = 1
            while True:
                num_personas = request.POST.get(f'num_personas_{i}')
                if num_personas is None:
                    break
                num_personas = int(num_personas) if num_personas else 0
                if num_personas > 0:
                    procedencia      = request.POST.get(f'procedencia_{i}', '')
                    lugar_especifico = request.POST.get(f'lugar_{i}', '')
                    if lugar_especifico in ('zona_costa', 'zona_sierra', 'zona_oriente'):
                        lugar_especifico = request.POST.get(f'lugar_texto_{i}', lugar_especifico)
                    elif lugar_especifico == 'otro_extranjero':
                        lugar_especifico = request.POST.get(f'lugar_texto_{i}', lugar_especifico)
                    tipo_visita       = request.POST.get(f'tipo_visita_{i}', 'individual')
                    rango_edad        = request.POST.get(f'rango_edad_{i}', '')
                    composicion_grupo = request.POST.get(f'composicion_{i}', '')
                    medio_transporte  = request.POST.get(f'transporte_{i}', '')
                    estadia_dias      = int(request.POST.get(f'dias_{i}') or 0)
                    estadia_noches    = int(request.POST.get(f'noches_{i}') or 0)
                    motivo_viaje      = request.POST.get(f'motivo_{i}', 'otros')
                    motivo_otro       = request.POST.get(f'motivo_otro_{i}', '').strip()
                    fecha = datetime(anio, mes, 28, 12, 0, 0)
                    RegistroTurista.objects.create(
                        tipo_visita       = tipo_visita,
                        num_personas      = num_personas,
                        procedencia       = procedencia,
                        lugar_especifico  = lugar_especifico,
                        rango_edad        = rango_edad,
                        medio_transporte  = medio_transporte,
                        composicion_grupo = composicion_grupo,
                        estadia_dias      = estadia_dias,
                        estadia_noches    = estadia_noches,
                        motivo_viaje      = motivo_viaje,
                        motivo_otro       = motivo_otro if motivo_viaje == 'otros' else '',
                        fecha_registro    = fecha,
                    )
                    guardados += 1
                i += 1
            messages.success(request, f'✅ {guardados} registro(s) de {MESES[mes-1].capitalize()} {anio} guardados correctamente.')

    return redirect('formulario_registro')


@login_required
def todas_las_entradas(request):
    registros = RegistroTurista.objects.all().order_by('-fecha_registro', '-id')
    return render(request, 'turistas/todas_entradas.html', {'registros': registros})


@login_required
def reporte_turistas(request):
    anio = 2026
    qs   = RegistroTurista.objects.filter(fecha_registro__year=anio)

    # ── Procedencias ──
    nac_dict = {r['lugar_especifico']: r['total']
                for r in qs.filter(procedencia='nacional')
                           .values('lugar_especifico')
                           .annotate(total=Sum('num_personas'))}
    proc_nac_labels = [LUGARES_LABELS.get(l, l.title()) for l in LUGARES_NACIONALES]
    proc_nac_data   = [nac_dict.get(l, 0) for l in LUGARES_NACIONALES]

    lugres_ext = [k for k in LUGARES_LABELS if k not in LUGARES_NACIONALES]
    int_dict   = {r['lugar_especifico']: r['total']
                  for r in qs.filter(procedencia='extranjero')
                             .values('lugar_especifico')
                             .annotate(total=Sum('num_personas'))}
    proc_int_labels = [LUGARES_LABELS.get(l, l.title()) for l in lugres_ext]
    proc_int_data   = [int_dict.get(l, 0) for l in lugres_ext]

    total_nac = qs.filter(procedencia='nacional').aggregate(t=Sum('num_personas'))['t'] or 0
    total_ext = qs.filter(procedencia='extranjero').aggregate(t=Sum('num_personas'))['t'] or 0
    total_gen = total_nac + total_ext
    pct_nac   = int(round(total_nac / total_gen * 100)) if total_gen else 0
    pct_ext   = int(round(total_ext / total_gen * 100)) if total_gen else 0

    # ── Motivos ──
    motivos_dict = {r['motivo_viaje']: r['total']
                    for r in qs.values('motivo_viaje').annotate(total=Sum('num_personas'))}
    dem_labels = list(MOTIVOS_LABELS.values())
    dem_data   = [motivos_dict.get(k, 0) for k in MOTIVOS_LABELS.keys()]
    dem_keys   = list(MOTIVOS_LABELS.keys())

    # ── Flujo mensual ──
    flujo_qs   = (qs.annotate(mes=TruncMonth('fecha_registro'))
                    .values('mes').annotate(total=Sum('num_personas')).order_by('mes'))
    flujo_dict = {r['mes'].month: r['total'] for r in flujo_qs if r['mes']}
    flujo_data = [flujo_dict.get(i, 0) for i in range(1, 13)]

    # ── Tipo de visita ──
    tipo_dict          = {r['tipo_visita']: r['total'] for r in qs.values('tipo_visita').annotate(total=Sum('num_personas'))}
    tipo_visita_labels = ['Visitantes', 'Grupo']
    tipo_visita_data   = [tipo_dict.get('individual', 0), tipo_dict.get('grupo', 0)]

    # ── Rango de edad ──
    edad_dict   = {r['rango_edad']: r['total'] for r in qs.values('rango_edad').annotate(total=Sum('num_personas'))}
    edad_labels = ['Jóvenes 16-25', 'Adultos 26-50', '51+ años']
    edad_data   = [edad_dict.get('jovenes', 0), edad_dict.get('adultos', 0), edad_dict.get('adultos_mayores', 0)]

    # ── Transporte ──
    transp_dict        = {r['medio_transporte']: r['total'] for r in qs.values('medio_transporte').annotate(total=Sum('num_personas'))}
    transporte_labels  = ['Vehículo Propio', 'Bus Público', 'Transporte Turístico']
    transporte_data    = [transp_dict.get('vehiculo_propio', 0), transp_dict.get('bus_publico', 0), transp_dict.get('transporte_turistico', 0)]

    # ── Composición del grupo ──
    comp_dict          = {r['composicion_grupo']: r['total'] for r in qs.values('composicion_grupo').annotate(total=Sum('num_personas'))}
    composicion_labels = ['En Pareja', 'En Familia', 'Con Amigos', 'Trabajo']
    composicion_data   = [comp_dict.get('pareja', 0), comp_dict.get('familia', 0), comp_dict.get('amigos', 0), comp_dict.get('trabajo', 0)]

    # ── Estadía promedio ──
    estadia    = qs.aggregate(avg_dias=Avg('estadia_dias'), avg_noches=Avg('estadia_noches'))
    avg_dias   = int(round(estadia['avg_dias'] or 0))
    avg_noches = int(round(estadia['avg_noches'] or 0))

    # ── Tablas ──
    total_visitantes_mes, total_grupos_mes, total_individual_mes = [], [], []
    for i in range(1, 13):
        total_visitantes_mes.append(
            qs.filter(fecha_registro__month=i).aggregate(t=Sum('num_personas'))['t'] or 0)
        total_grupos_mes.append(
            qs.filter(fecha_registro__month=i, tipo_visita='grupo').aggregate(t=Sum('num_personas'))['t'] or 0)
        total_individual_mes.append(
            qs.filter(fecha_registro__month=i, tipo_visita='individual').aggregate(t=Sum('num_personas'))['t'] or 0)

    tabla_anual = []
    for key, label in MOTIVOS_LABELS.items():
        fila = {'motivo': label, 'meses': [], 'total': 0}
        for i in range(1, 13):
            val = qs.filter(motivo_viaje=key, fecha_registro__month=i).aggregate(t=Sum('num_personas'))['t'] or 0
            fila['meses'].append(val)
            fila['total'] += val
        tabla_anual.append(fila)

    reporte_diario_detalle = (qs
        .values('fecha_registro__date', 'procedencia', 'lugar_especifico', 'motivo_viaje', 'tipo_visita')
        .annotate(total_personas=Sum('num_personas'), total_grupos=Count('id'))
        .order_by('-fecha_registro__date'))

    mes_sel = int(request.GET.get('mes', date.today().month))
    reporte_mensual = (qs.filter(fecha_registro__month=mes_sel)
                         .values('lugar_especifico', 'motivo_viaje', 'procedencia', 'tipo_visita')
                         .annotate(total_personas=Sum('num_personas'), total_grupos=Count('id'))
                         .order_by('-total_personas'))
    mensual_motivos = [
        {'motivo': label, 'total': qs.filter(motivo_viaje=key, fecha_registro__month=mes_sel).aggregate(t=Sum('num_personas'))['t'] or 0}
        for key, label in MOTIVOS_LABELS.items()
    ]

    # ── Todos los registros para filtro JS ──
    todos = qs.values('num_personas', 'procedencia', 'lugar_especifico',
                      'motivo_viaje', 'tipo_visita', 'rango_edad',
                      'medio_transporte', 'composicion_grupo',
                      'estadia_dias', 'estadia_noches', 'fecha_registro')

    datos_por_mes_js = json.dumps([{
        'anio':           r['fecha_registro'].year,
        'mes':            r['fecha_registro'].month,
        'fecha':          r['fecha_registro'].strftime('%Y-%m-%d'),
        'num_personas':   r['num_personas'],
        'num_grupos':     1 if r['tipo_visita'] == 'grupo' else 0,
        'procedencia':    r['procedencia'],
        'lugar':          r['lugar_especifico'],
        'motivo':         r['motivo_viaje'],
        'tipo_visita':    r['tipo_visita'],
        'rango_edad':     r['rango_edad'] or '',
        'transporte':     r['medio_transporte'] or '',
        'composicion':    r['composicion_grupo'] or '',
        'estadia_dias':   r['estadia_dias'] or 0,
        'estadia_noches': r['estadia_noches'] or 0,
    } for r in todos])

    context = {
        'proc_nac_labels':        json.dumps(proc_nac_labels),
        'proc_nac_data':          json.dumps(proc_nac_data),
        'proc_nac_keys':          json.dumps(LUGARES_NACIONALES),
        'proc_int_labels':        json.dumps(proc_int_labels),
        'proc_int_data':          json.dumps(proc_int_data),
        'proc_int_keys':          json.dumps(lugres_ext),
        'pct_nac':                pct_nac,
        'pct_ext':                pct_ext,
        'total_nac':              total_nac,
        'total_ext':              total_ext,
        'dem_labels':             json.dumps(dem_labels),
        'dem_data':               json.dumps(dem_data),
        'dem_keys':               json.dumps(dem_keys),
        'flujo_data':             json.dumps(flujo_data),
        'tipo_visita_labels':     json.dumps(tipo_visita_labels),
        'tipo_visita_data':       json.dumps(tipo_visita_data),
        'edad_labels':            json.dumps(edad_labels),
        'edad_data':              json.dumps(edad_data),
        'transporte_labels':      json.dumps(transporte_labels),
        'transporte_data':        json.dumps(transporte_data),
        'composicion_labels':     json.dumps(composicion_labels),
        'composicion_data':       json.dumps(composicion_data),
        'avg_dias':               avg_dias,
        'avg_noches':             avg_noches,
        'tabla_anual':            tabla_anual,
        'total_visitantes_mes':   total_visitantes_mes,
        'total_individual_mes':   total_individual_mes,
        'total_grupos_mes':       total_grupos_mes,
        'total_visitantes_anual': sum(total_visitantes_mes),
        'total_individual_anual': sum(total_individual_mes),
        'total_grupos_anual':     sum(total_grupos_mes),
        'meses':                  MESES,
        'reporte_diario_detalle': reporte_diario_detalle,
        'reporte_mensual':        reporte_mensual,
        'mensual_motivos':        mensual_motivos,
        'mes_sel':                mes_sel,
        'mes_sel_nombre':         MESES[mes_sel - 1].capitalize(),
        'meses_lista':            [(i+1, m.capitalize()) for i, m in enumerate(MESES)],
        'datos_por_mes':          datos_por_mes_js,
    }
    return render(request, 'turistas/reporte.html', context)