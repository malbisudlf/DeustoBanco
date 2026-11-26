from functools import wraps

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login as iniciar_sesion
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.db.models import Sum
from django.urls import reverse
from django.utils.cache import patch_vary_headers
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView, ListView, TemplateView
from .models import Cliente, Cuenta, Tarjeta, Movimiento
from .forms import AltaClienteForm, FiltroMovimientosForm, MovimientoForm


def acceso_empleado(permiso):
    def decorar(vista):
        @never_cache
        @login_required
        @wraps(vista)
        def comprobar(request, *args, **kwargs):
            if not request.user.is_staff or not request.user.has_perm(permiso):
                raise PermissionDenied
            return vista(request, *args, **kwargs)

        return comprobar

    return decorar


def index(request):
    return render(request, 'index.html')


@method_decorator(acceso_empleado('appBanco.view_cliente'), name='dispatch')
class ClientesListView(ListView):
    model = Cliente
    context_object_name = 'clientes_listado'
    template_name = 'lista_clientes.html'


@method_decorator(acceso_empleado('appBanco.view_cliente'), name='dispatch')
class ClienteDetailView(DetailView):
    model = Cliente
    context_object_name = 'cliente'
    template_name = 'detalle_cliente.html'

    def get_queryset(self):
        if not self.request.user.has_perm('appBanco.view_cuenta'):
            return super().get_queryset()
        return Cliente.objects.annotate(saldo_total=Sum('cuentas__saldo', default=0))


@acceso_empleado('appBanco.view_cuenta')
def lista_cuentas(request):
    cuentas = Cuenta.objects.select_related('cliente')
    context = {'cuentas_listado': cuentas}
    return render(request, 'lista_cuentas.html', context)


@acceso_empleado('appBanco.view_cuenta')
def detalle_cuenta(request, pk):
    cuenta = get_object_or_404(Cuenta, pk=pk)
    form = MovimientoForm()
    if request.method == 'POST':
        if not request.user.has_perm('appBanco.add_movimiento'):
            raise PermissionDenied
        form = MovimientoForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.cuenta = cuenta
            movimiento.save()
            messages.success(request, f'{movimiento.get_tipo_display()} registrado. El saldo se ha actualizado.')
            return redirect('detalle_cuenta', pk=cuenta.pk)
    context = {'cuenta': cuenta, 'form': form}
    return render(request, 'detalle_cuenta.html', context)


@method_decorator(acceso_empleado('appBanco.view_tarjeta'), name='dispatch')
class TarjetasListView(ListView):
    model = Tarjeta
    context_object_name = 'tarjetas_listado'
    template_name = 'lista_tarjetas.html'

    def get_queryset(self):
        return Tarjeta.objects.select_related('cuenta')


@method_decorator(acceso_empleado('appBanco.view_tarjeta'), name='dispatch')
class TarjetaDetailView(DetailView):
    model = Tarjeta
    context_object_name = 'tarjeta'
    template_name = 'detalle_tarjeta.html'


@acceso_empleado('appBanco.view_movimiento')
def lista_movimientos(request):
    filtro = FiltroMovimientosForm(request.GET)
    movimientos = Movimiento.objects.select_related('cuenta').order_by('-fecha', '-pk')
    if filtro.is_valid():
        tipo = filtro.cleaned_data['tipo']
        desde = filtro.cleaned_data['desde']
        hasta = filtro.cleaned_data['hasta']
        if tipo:
            movimientos = movimientos.filter(tipo=tipo)
        if desde:
            movimientos = movimientos.filter(fecha__gte=desde)
        if hasta:
            movimientos = movimientos.filter(fecha__lte=hasta)
    else:
        movimientos = movimientos.none()
    context = {'movimientos_listado': movimientos, 'filtro': filtro}

    # jQuery marca sus peticiones AJAX con esta cabecera: en ese caso basta con devolver
    # el fragmento de la tabla; si no, se devuelve la página completa (funciona sin JavaScript).
    es_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    plantilla = 'parciales/resultados_movimientos.html' if es_ajax else 'lista_movimientos.html'
    respuesta = render(request, plantilla, context)
    patch_vary_headers(respuesta, ['X-Requested-With'])
    return respuesta


@acceso_empleado('appBanco.view_movimiento')
def detalle_movimiento(request, pk):
    movimiento = get_object_or_404(Movimiento, pk=pk)
    context = {'movimiento': movimiento}
    return render(request, 'detalle_movimiento.html', context)


@never_cache
def alta_cliente(request):
    if request.user.is_authenticated:
        return redirect('principal' if request.user.is_staff else 'mi_cuenta')

    form = AltaClienteForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        try:
            usuario = form.crear_cliente()
        except IntegrityError:
            form.add_error(None, 'No se pudo completar el alta. Revisa el usuario o el correo y vuelve a intentarlo.')
        else:
            iniciar_sesion(request, usuario)
            messages.success(request, 'Tu cuenta está lista.')
            return redirect('mi_cuenta')

    return render(request, 'registro/alta_cliente.html', {'form': form})


@never_cache
@login_required
def mi_cuenta(request):
    cuentas = Cuenta.objects.filter(cliente__usuario=request.user).order_by('fecha_apertura', 'pk')
    tarjetas = Tarjeta.objects.filter(cuenta__in=cuentas).order_by('pk')
    movimientos = Movimiento.objects.filter(cuenta__in=cuentas).order_by('-fecha', '-pk')[:10]
    return render(request, 'registro/mi_cuenta.html', {
        'cuentas': cuentas, 'tarjetas': tarjetas, 'movimientos': movimientos,
    })


class InicioSesionView(auth_views.LoginView):
    template_name = 'registro/login.html'

    def get_default_redirect_url(self):
        return reverse('principal' if self.request.user.is_staff else 'mi_cuenta')


login = InicioSesionView.as_view()
logout = auth_views.LogoutView.as_view()
pagina_sobre = TemplateView.as_view(template_name='estaticas/sobre.html')
pagina_becas_promociones = TemplateView.as_view(template_name='estaticas/becas_promociones.html')
pagina_contacto = TemplateView.as_view(template_name='estaticas/contacto.html')
pagina_aviso_demo = TemplateView.as_view(template_name='estaticas/aviso_demo.html')
