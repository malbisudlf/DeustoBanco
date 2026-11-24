from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Cliente, Cuenta, Movimiento


class ListadoMovimientosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cliente = Cliente.objects.create(nombre='Ana', apellidos='Pérez', email='ana@example.test')
        cuenta = Cuenta.objects.create(cliente=cliente, iban='ES000001')
        cls.gasto_inicial = Movimiento.objects.create(
            cuenta=cuenta, concepto='Cine', tipo='gasto', importe=Decimal('9.50'), fecha=date(2026, 11, 1),
        )
        cls.ingreso = Movimiento.objects.create(
            cuenta=cuenta, concepto='Nómina', tipo='ingreso', importe=Decimal('100'), fecha=date(2026, 11, 15),
        )
        cls.gasto_final = Movimiento.objects.create(
            cuenta=cuenta, concepto='Tren', tipo='gasto', importe=Decimal('22.50'), fecha=date(2026, 11, 30),
        )
        cls.gasto_posterior = Movimiento.objects.create(
            cuenta=cuenta, concepto='Comida', tipo='gasto', importe=Decimal('15'), fecha=date(2026, 12, 1),
        )

    def test_listado_ordenado_con_fecha_e_importe(self):
        respuesta = self.client.get(reverse('lista_movimientos'))

        self.assertQuerySetEqual(
            respuesta.context['movimientos_listado'],
            [self.gasto_posterior, self.gasto_final, self.ingreso, self.gasto_inicial],
        )
        self.assertContains(respuesta, '30/11/2026')
        self.assertContains(respuesta, '22.50 €')

    def test_combina_tipo_y_rango_inclusivo(self):
        respuesta = self.client.get(reverse('lista_movimientos'), {
            'tipo': 'gasto', 'desde': '2026-11-01', 'hasta': '2026-11-30',
        })

        self.assertQuerySetEqual(respuesta.context['movimientos_listado'], [self.gasto_final, self.gasto_inicial])

    def test_admite_una_sola_fecha(self):
        respuesta = self.client.get(reverse('lista_movimientos'), {'desde': '2026-11-30'})

        self.assertQuerySetEqual(respuesta.context['movimientos_listado'], [self.gasto_posterior, self.gasto_final])

    def test_muestra_un_error_para_filtros_invalidos(self):
        casos = [
            ({'desde': '2026-11-30', 'hasta': '2026-11-01'}, 'posterior'),
            ({'hasta': '2026-02-30'}, 'fecha de fin válida'),
            ({'tipo': 'otro'}, 'tipo de movimiento válido'),
        ]
        for filtros, mensaje in casos:
            with self.subTest(filtros=filtros):
                respuesta = self.client.get(reverse('lista_movimientos'), filtros)

                self.assertContains(respuesta, mensaje)
                self.assertNotContains(respuesta, 'data-movimiento')
