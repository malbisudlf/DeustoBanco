from django.urls import path
from . import views


urlpatterns = [
    path('primeravista', views.index, name='index'),
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/<int:pk>/', views.detalle_cliente, name='detalle_cliente'),
    path('cuentas/', views.lista_cuentas, name='lista_cuentas'),
    path('cuentas/<int:pk>/', views.detalle_cuenta, name='detalle_cuenta'),
    path('tarjetas/', views.lista_tarjetas, name='lista_tarjetas'),
    path('tarjetas/<int:pk>/', views.detalle_tarjeta, name='detalle_tarjeta'),
    path('movimientos/', views.lista_movimientos, name='lista_movimientos'),
    path('movimientos/<int:pk>/', views.detalle_movimiento, name='detalle_movimiento'),
    path('sobre/', views.pagina_sobre, name='sobre'),
    path('contacto/', views.pagina_contacto, name='contacto'),
    path('accounts/login/', views.login, name='login'),
    path('accounts/logout/', views.logout, name='logout'),
]
