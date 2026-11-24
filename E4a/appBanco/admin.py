from django.contrib import admin
from .models import Cliente, Cuenta, Tarjeta, Movimiento


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellidos', 'email', 'telefono', 'fecha_alta')
    search_fields = ('nombre', 'apellidos', 'email')
    list_filter = ('fecha_alta',)
    ordering = ('apellidos', 'nombre')


@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ('iban', 'cliente', 'tipo', 'saldo', 'fecha_apertura')
    search_fields = ('iban', 'cliente__nombre', 'cliente__apellidos')
    list_filter = ('tipo', 'fecha_apertura')
    list_select_related = ('cliente',)


@admin.register(Tarjeta)
class TarjetaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'cuenta', 'tipo', 'fecha_caducidad', 'activa', 'limite_diario')
    search_fields = ('numero', 'cuenta__iban')
    list_filter = ('tipo', 'activa', 'fecha_caducidad')
    list_select_related = ('cuenta',)


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'concepto', 'cuenta', 'tipo', 'importe')
    search_fields = ('concepto', 'cuenta__iban')
    list_filter = ('tipo', 'fecha')
    date_hierarchy = 'fecha'
    ordering = ('-fecha', '-pk')
    list_select_related = ('cuenta',)
