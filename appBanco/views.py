from django.shortcuts import render, get_object_or_404
from .models import Cliente, Cuenta, Tarjeta, Movimiento

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
    context = {'cuenta': cuenta}
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
