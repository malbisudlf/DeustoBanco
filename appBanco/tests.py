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


class SaldoCuentaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cliente = Cliente.objects.create(nombre='César Manuel', apellidos='Prueba', email='cesar@example.test')
        cls.cuenta = Cuenta.objects.create(cliente=cls.cliente, iban='ES000002', saldo=Decimal('100'))
        cls.ahorro = Cuenta.objects.create(cliente=cls.cliente, iban='ES000003', saldo=Decimal('300'))

    def assertSaldos(self, corriente, ahorro):
        self.cuenta.refresh_from_db()
        self.ahorro.refresh_from_db()
        self.assertEqual(self.cuenta.saldo, Decimal(corriente))
        self.assertEqual(self.ahorro.saldo, Decimal(ahorro))

    def test_ingreso_y_gasto_desde_el_formulario_actualizan_la_cuenta_y_el_total(self):
        url = reverse('detalle_cuenta', args=[self.cuenta.pk])
        ingreso = self.client.post(url, {
            'concepto': 'Ingreso de prueba', 'tipo': 'ingreso', 'importe': '50.00', 'fecha': '2026-11-24',
        }, follow=True)

        self.assertRedirects(ingreso, url)
        self.assertContains(ingreso, 'Ingreso registrado. El saldo se ha actualizado.')
        self.assertContains(ingreso, '150.00 €')
        self.assertSaldos('150', '300')

        gasto = self.client.post(url, {
            'concepto': 'Gasto de prueba', 'tipo': 'gasto', 'importe': '20.00', 'fecha': '2026-11-24',
        }, follow=True)

        self.assertRedirects(gasto, url)
        self.assertContains(gasto, 'Gasto registrado. El saldo se ha actualizado.')
        self.client.get(url)
        self.assertEqual(self.cuenta.movimientos.count(), 2)
        self.assertSaldos('130', '300')
        cliente = self.client.get(reverse('detalle_cliente', args=[self.cliente.pk]))
        self.assertContains(cliente, 'Saldo total: 430.00 €')

    def test_formulario_muestra_calendario_y_avisa_si_faltan_datos(self):
        url = reverse('detalle_cuenta', args=[self.cuenta.pk])

        pagina = self.client.get(url)
        self.assertContains(pagina, 'type="date"')
        self.assertIsNotNone(pagina.context['form']['fecha'].value())

        respuesta = self.client.post(url, {'concepto': 'Prueba', 'tipo': 'ingreso', 'importe': '50'})
        self.assertContains(respuesta, 'No se ha guardado el movimiento.')
        self.assertContains(respuesta, 'Selecciona una fecha.')
        self.assertFalse(self.cuenta.movimientos.exists())
        self.assertSaldos('100', '300')

    def test_rechaza_importes_cero_o_negativos(self):
        for importe in ('0', '-10'):
            with self.subTest(importe=importe):
                resultado = self.client.post(reverse('detalle_cuenta', args=[self.cuenta.pk]), {
                    'concepto': 'Importe inválido', 'tipo': 'gasto', 'importe': importe, 'fecha': '2026-11-24',
                })

                self.assertContains(resultado, 'Introduce un importe mayor que cero.')
                self.assertFalse(self.cuenta.movimientos.exists())
                self.assertSaldos('100', '300')

    def test_editar_y_borrar_un_movimiento_corrige_el_saldo(self):
        movimiento = Movimiento.objects.create(
            cuenta=self.cuenta, concepto='Prueba', tipo='ingreso', importe=Decimal('50'), fecha=date(2026, 11, 24),
        )
        movimiento.importe = Decimal('20')
        movimiento.tipo = 'gasto'
        movimiento.save(update_fields=['importe', 'tipo'])
        self.assertSaldos('80', '300')

        movimiento.cuenta = self.ahorro
        movimiento.save(update_fields=['cuenta'])
        self.assertSaldos('100', '280')

        Movimiento.objects.filter(pk=movimiento.pk).delete()
        self.assertSaldos('100', '300')
