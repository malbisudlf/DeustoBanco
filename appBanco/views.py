from django.shortcuts import render, get_object_or_404
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from .models import Cliente, Cuenta, Tarjeta, Movimiento
from .forms import MovimientoForm


def index(request):
    return render(request, 'index.html')


def lista_clientes(request):
    clientes = Cliente.objects.all()
    context = {'clientes_listado': clientes}
    return render(request, 'lista_clientes.html', context)


def detalle_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    context = {'cliente': cliente}
    return render(request, 'detalle_cliente.html', context)


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
    context = {'cuenta': cuenta, 'form': form}
    return render(request, 'detalle_cuenta.html', context)


def lista_tarjetas(request):
    tarjetas = Tarjeta.objects.select_related('cuenta')
    context = {'tarjetas_listado': tarjetas}
    return render(request, 'lista_tarjetas.html', context)


def detalle_tarjeta(request, pk):
    tarjeta = get_object_or_404(Tarjeta, pk=pk)
    context = {'tarjeta': tarjeta}
    return render(request, 'detalle_tarjeta.html', context)


def lista_movimientos(request):
    movimientos = Movimiento.objects.select_related('cuenta')
    context = {'movimientos_listado': movimientos}
    return render(request, 'lista_movimientos.html', context)


def detalle_movimiento(request, pk):
    movimiento = get_object_or_404(Movimiento, pk=pk)
    context = {'movimiento': movimiento}
    return render(request, 'detalle_movimiento.html', context)


login = auth_views.LoginView.as_view(template_name='registro/login.html')
logout = auth_views.LogoutView.as_view()
pagina_sobre = TemplateView.as_view(template_name='estaticas/sobre.html')
pagina_contacto = TemplateView.as_view(template_name='estaticas/contacto.html')
