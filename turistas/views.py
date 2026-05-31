from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth, TruncDate
from .models import RegistroTurista
from datetime import date
import json

MOTIVOS_LABELS = {
    'hoteles':       'Hoteles',
    'campings':      'Campings',
    'apart_bungal':  'Apart/Bungal',
    'balnearios':    'Balnearios',
    'turismo_rural': 'Turismo Rural',
    'rutas_sender':  'Rutas/Sender',
    'par_naturales': 'Par. Naturales',
    'gastronomia':   'Gastronomía',
    'a_culturales':  'A. Culturales',
    'fiestas':       'Fiestas',
    'artesania':     'Artesanía',
    'ocio':          'Ocio',
    'a_deportiva':   'A. Deportiva',
    'transportes':   'Transportes',
    'info_local':    'Info Local',
    'c_azahar':      'C. Azahar',
    'c_blanca':      'C. Blanca',
    'benidorm':      'Benidorm',
    'otros':         'Otros',
}

MESES = ['enero','febrero','marzo','abril','mayo','junio',
         'julio','agosto','septiembre','octubre','noviembre','diciembre']

LUGARES_NACIONALES = [
    'cañar','el_tambo','suscal','biblián','cuenca','quito',
    'guayaquil','zona_sierra','zona_costa','zona_oriente','galápagos'
]

LUGARES_LABELS = {
    'cañar':'Cañar','el_tambo':'El Tambo','suscal':'Suscal',
    'biblián':'Biblián','cuenca':'Cuenca','quito':'Quito',
    'guayaquil':'Guayaquil','zona_sierra':'Zona Sierra',
    'zona_costa':'Zona Costa','zona_oriente':'Zona Oriente',
    'galápagos':'Galápagos','estados_unidos':'Estados Unidos',
    'américa_n':'América N.','américa_del_sur':'América del Sur',
    'austria':'Austria','bélgica':'Bélgica','escandinavia':'Escandinavia',
    'francia':'Francia','holanda':'Holanda','italia':'Italia',
    'países_asiáticos':'Países Asiáticos','países_del_este':'Países del Este',
    'portugal':'Portugal','reino_unido':'Reino Unido',
    'suiza':'Suiza','baleares':'Baleares','otros':'Otros',
}


# 1. FORMULARIO DE REGISTRO
@login_required
def formulario_registro(request, id_registro=None):
    registro = None
    if id_registro:
        registro = get_object_or_404(RegistroTurista, id=id_registro)

    if request.method == 'POST':
        num_personas     = request.POST.get('num_personas')
        procedencia      = request.POST.get('procedencia')
        lugar_especifico = request.POST.get('lugar_especifico')
        motivo_viaje     = request.POST.get('motivo_viaje')

        if registro:
            registro.num_personas     = num_personas
            registro.procedencia      = procedencia
            registro.lugar_especifico = lugar_especifico
            registro.motivo_viaje     = motivo_viaje
            registro.save()
            messages.success(request, '¡Registro editado y actualizado correctamente!')
        else:
            RegistroTurista.objects.create(
                num_personas=num_personas,
                procedencia=procedencia,
                lugar_especifico=lugar_especifico,
                motivo_viaje=motivo_viaje
            )
            messages.success(request, '¡Registro guardado exitosamente!')

        return redirect('formulario_registro')

    registros = RegistroTurista.objects.filter(fecha_registro__date=date.today()).order_by('-id')
    return render(request, 'turistas/formulario.html', {
        'registro':      registro,
        'registros':     registros,
        'motivos_lista': MOTIVOS_LABELS.items(),
    })


# 2. ELIMINAR REGISTRO
@login_required
def eliminar_registro(request, id_registro):
    registro = get_object_or_404(RegistroTurista, id=id_registro)
    registro.delete()
    messages.success(request, '¡Registro eliminado correctamente!')
    return redirect('formulario_registro')


# 3. REPORTES CON GRÁFICOS
@login_required
def reporte_turistas(request):
    año = 2026
    qs  = RegistroTurista.objects.filter(fecha_registro__year=año)

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
    pct_nac   = round(total_nac / total_gen * 100, 1) if total_gen else 0
    pct_ext   = round(total_ext / total_gen * 100, 1) if total_gen else 0

    motivos_dict = {r['motivo_viaje']: r['total']
                    for r in qs.values('motivo_viaje').annotate(total=Sum('num_personas'))}
    dem_labels = list(MOTIVOS_LABELS.values())
    dem_data   = [motivos_dict.get(k, 0) for k in MOTIVOS_LABELS.keys()]
    dem_keys   = list(MOTIVOS_LABELS.keys())

    flujo_qs   = (qs.annotate(mes=TruncMonth('fecha_registro'))
                    .values('mes').annotate(total=Sum('num_personas')).order_by('mes'))
    flujo_dict = {r['mes'].month: r['total'] for r in flujo_qs if r['mes']}
    flujo_data = [flujo_dict.get(i, 0) for i in range(1, 13)]

    total_visitantes_mes, total_grupos_mes = [], []
    for i in range(1, 13):
        total_visitantes_mes.append(
            qs.filter(fecha_registro__month=i).aggregate(t=Sum('num_personas'))['t'] or 0)
        total_grupos_mes.append(
            qs.filter(fecha_registro__month=i).aggregate(t=Count('id'))['t'] or 0)

    tabla_anual = []
    for key, label in MOTIVOS_LABELS.items():
        fila = {'motivo': label, 'meses': [], 'total': 0}
        for i in range(1, 13):
            val = qs.filter(motivo_viaje=key, fecha_registro__month=i).aggregate(
                t=Sum('num_personas'))['t'] or 0
            fila['meses'].append(val)
            fila['total'] += val
        tabla_anual.append(fila)

    reporte_diario_detalle = (qs
        .values('fecha_registro__date', 'procedencia', 'lugar_especifico', 'motivo_viaje')
        .annotate(total_personas=Sum('num_personas'), total_grupos=Count('id'))
        .order_by('-fecha_registro__date'))

    mes_sel = int(request.GET.get('mes', 4))
    reporte_mensual = (qs.filter(fecha_registro__month=mes_sel)
                         .values('lugar_especifico', 'motivo_viaje', 'procedencia')
                         .annotate(total_personas=Sum('num_personas'), total_grupos=Count('id'))
                         .order_by('-total_personas'))
    mensual_motivos = [
        {'motivo': label,
         'total':  qs.filter(motivo_viaje=key, fecha_registro__month=mes_sel)
                     .aggregate(t=Sum('num_personas'))['t'] or 0}
        for key, label in MOTIVOS_LABELS.items()
    ]

    todos = qs.values('num_personas', 'procedencia', 'lugar_especifico',
                      'motivo_viaje', 'fecha_registro')

    datos_por_mes_js = json.dumps([{
        'año':          r['fecha_registro'].year,
        'mes':          r['fecha_registro'].month,
        'fecha':        r['fecha_registro'].strftime('%Y-%m-%d'),
        'num_personas': r['num_personas'],
        'procedencia':  r['procedencia'],
        'lugar':        r['lugar_especifico'],
        'motivo':       r['motivo_viaje'],
    } for r in todos])

    context = {
        'proc_nac_labels': json.dumps(proc_nac_labels),
        'proc_nac_data':   json.dumps(proc_nac_data),
        'proc_nac_keys':   json.dumps(LUGARES_NACIONALES),
        'proc_int_labels': json.dumps(proc_int_labels),
        'proc_int_data':   json.dumps(proc_int_data),
        'proc_int_keys':   json.dumps(lugres_ext),
        'pct_nac':         pct_nac,
        'pct_ext':         pct_ext,
        'total_nac':       total_nac,
        'total_ext':       total_ext,
        'dem_labels':      json.dumps(dem_labels),
        'dem_data':        json.dumps(dem_data),
        'dem_keys':        json.dumps(dem_keys),
        'flujo_data':      json.dumps(flujo_data),
        'tabla_anual':              tabla_anual,
        'total_visitantes_mes':     total_visitantes_mes,
        'total_grupos_mes':         total_grupos_mes,
        'total_visitantes_anual':   sum(total_visitantes_mes),
        'total_grupos_anual':       sum(total_grupos_mes),
        'meses':                    MESES,
        'reporte_diario_detalle':   reporte_diario_detalle,
        'reporte_mensual':          reporte_mensual,
        'mensual_motivos':          mensual_motivos,
        'mes_sel':                  mes_sel,
        'mes_sel_nombre':           MESES[mes_sel - 1].capitalize(),
        'meses_lista':              [(i+1, m.capitalize()) for i, m in enumerate(MESES)],
        'datos_por_mes':            datos_por_mes_js,
    }
    return render(request, 'turistas/reporte.html', context)


# 4. GUARDAR DATOS PERSONALIZADOS
@login_required
def guardar_datos_personalizados(request):
    if request.method == 'POST':
        mes              = int(request.POST.get('mes'))
        año              = int(request.POST.get('año'))
        procedencia      = request.POST.get('procedencia')
        lugar_especifico = request.POST.get('lugar_especifico')
        fecha            = date(año, mes, 1)

        for motivo in MOTIVOS_LABELS.keys():
            cantidad = int(request.POST.get(f'motivo_{motivo}', 0))
            if cantidad > 0:
                RegistroTurista.objects.create(
                    num_personas=cantidad,
                    procedencia=procedencia,
                    lugar_especifico=lugar_especifico,
                    motivo_viaje=motivo,
                    fecha_registro=fecha
                )

        messages.success(request, f'✅ Datos de {mes}/{año} guardados correctamente.')
    return redirect('formulario_registro')


# 5. TODAS LAS ENTRADAS
@login_required
def todas_las_entradas(request):
    registros = RegistroTurista.objects.all().order_by('-fecha_registro', '-id')
    return render(request, 'turistas/todas_entradas.html', {
        'registros': registros,
    })