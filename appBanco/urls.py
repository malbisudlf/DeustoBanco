from django.urls import path
from . import views


urlpatterns = [
    path('primeravista', views.index, name='index'),
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/<int:id>/', views.detalle_cliente, name='detalle_cliente'),
]
