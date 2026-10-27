from django.urls import path
from . import views


urlpatterns = [
    path('primeravista', views.index, name='primeraURL'),
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/<int:pk>/', views.detalle_cliente, name='detalle_cliente'),
]
