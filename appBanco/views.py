from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Cliente

def index(request):
    return HttpResponse('primera vista funcionando correctamente')

def lista_clientes(request):
    clientes = Cliente.objects.all()
    context = {'clientes_listado': clientes}
    return render(request, 'lista_clientes.html', context)

def detalle_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    context = {'cliente': cliente}
    return render(request, 'detalle_cliente.html', context)