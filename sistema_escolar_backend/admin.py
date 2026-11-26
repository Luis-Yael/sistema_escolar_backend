from django.contrib import admin
from django.utils import timezone
from sistema_escolar_backend.models import Administradores, Maestros, Alumnos

# Textos que aparecen en la parte superior y en la pestaña del navegador
admin.site.site_header = "Sistema Escolar - Administración"
admin.site.site_title = "Sistema Escolar"
admin.site.index_title = "Panel de administración"


class PerfilAdmin(admin.ModelAdmin):
    # Configuración común para los tres tipos de perfil (administrador, maestro y alumno).
    # Cada clase hija agrega lo que es propio de su modelo.

    # Columnas de la tabla de listado
    list_display = ("id", "nombre_completo", "correo", "activo", "creation", "update")
    # Columnas que funcionan como enlace para abrir el registro
    list_display_links = ("id", "nombre_completo")
    # Filtros del panel lateral derecho
    list_filter = ("user__is_active", "creation")
    # Campos que recorre la barra de búsqueda (se puede navegar la relación con __)
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")
    ordering = ("id",)
    list_per_page = 20
    # Muestra un buscador en lugar de un desplegable enorme de usuarios
    autocomplete_fields = ("user",)
    # Campos que se muestran pero no se pueden editar
    readonly_fields = ("creation", "update")
    # Evita una consulta extra por fila al mostrar los datos del usuario
    list_select_related = ("user",)

    @admin.display(description="Nombre", ordering="user__first_name")
    def nombre_completo(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    @admin.display(description="Correo", ordering="user__email")
    def correo(self, obj):
        return obj.user.email

    @admin.display(description="Activo", boolean=True, ordering="user__is_active")
    def activo(self, obj):
        return obj.user.is_active

    def save_model(self, request, obj, form, change):
        # Al editar un registro existente se guarda la fecha de actualización
        if change:
            obj.update = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(Administradores)
class AdministradoresAdmin(PerfilAdmin):
    list_display = PerfilAdmin.list_display + ("clave_admin", "ocupacion")
    search_fields = PerfilAdmin.search_fields + ("clave_admin", "rfc")


@admin.register(Maestros)
class MaestrosAdmin(PerfilAdmin):
    list_display = PerfilAdmin.list_display + ("id_trabajador", "area_investigacion")
    search_fields = PerfilAdmin.search_fields + ("id_trabajador", "rfc", "area_investigacion")
    list_filter = PerfilAdmin.list_filter + ("area_investigacion",)


@admin.register(Alumnos)
class AlumnosAdmin(PerfilAdmin):
    list_display = PerfilAdmin.list_display + ("matricula", "ocupacion")
    search_fields = PerfilAdmin.search_fields + ("matricula", "curp", "rfc")

