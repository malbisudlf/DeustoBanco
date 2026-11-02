from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Cliente, Cuenta

def index(request):
    return HttpResponse('primera vista funcionando correctamente')

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