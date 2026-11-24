from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.db.models import Sum
from django.views.generic import DetailView, ListView, TemplateView
from .models import Cliente, Cuenta, Tarjeta, Movimiento
from .forms import FiltroMovimientosForm, MovimientoForm


def index(request):
    return render(request, 'index.html')


class ClientesListView(ListView):
    model = Cliente
    context_object_name = 'clientes_listado'
    template_name = 'lista_clientes.html'


class ClienteDetailView(DetailView):
    model = Cliente
    context_object_name = 'cliente'
    template_name = 'detalle_cliente.html'

    def get_queryset(self):
        return Cliente.objects.annotate(saldo_total=Sum('cuentas__saldo', default=0))


def lista_cuentas(request):
    cuentas = Cuenta.objects.select_related('cliente')
    context = {'cuentas_listado': cuentas}
    return render(request, 'lista_cuentas.html', context)


def detalle_cuenta(request, pk):
    cuenta = get_object_or_404(Cuenta, pk=pk)
    form = MovimientoForm()
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.cuenta = cuenta
            movimiento.save()
            messages.success(request, f'{movimiento.get_tipo_display()} registrado. El saldo se ha actualizado.')
            return redirect('detalle_cuenta', pk=cuenta.pk)
    context = {'cuenta': cuenta, 'form': form}
    return render(request, 'detalle_cuenta.html', context)


class TarjetasListView(ListView):
    model = Tarjeta
    context_object_name = 'tarjetas_listado'
    template_name = 'lista_tarjetas.html'

    def get_queryset(self):
        return Tarjeta.objects.select_related('cuenta')


class TarjetaDetailView(DetailView):
    model = Tarjeta
    context_object_name = 'tarjeta'
    template_name = 'detalle_tarjeta.html'


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
    return render(request, 'lista_movimientos.html', context)


def detalle_movimiento(request, pk):
    movimiento = get_object_or_404(Movimiento, pk=pk)
    context = {'movimiento': movimiento}
    return render(request, 'detalle_movimiento.html', context)


login = auth_views.LoginView.as_view(template_name='registro/login.html')
logout = auth_views.LogoutView.as_view()
pagina_sobre = TemplateView.as_view(template_name='estaticas/sobre.html')
pagina_contacto = TemplateView.as_view(template_name='estaticas/contacto.html')
