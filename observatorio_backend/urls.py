from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from turistas.views import formulario_registro, reporte_turistas, eliminar_registro, guardar_datos_personalizados, todas_las_entradas

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='turistas/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', formulario_registro, name='formulario_registro'),
    path('reportes/', reporte_turistas, name='reporte_turistas'),
    path('reportes/editar/<int:id_registro>/', formulario_registro, name='editar_turista'),
    path('reportes/eliminar/<int:id_registro>/', eliminar_registro, name='eliminar_registro'),
    path('guardar-personalizado/', guardar_datos_personalizados, name='guardar_datos_personalizados'),
    path('entradas/', todas_las_entradas, name='todas_las_entradas'),
]