from datetime import date
from decimal import Decimal

from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase
from django.urls import reverse

from .models import Cliente, Cuenta, Movimiento, Tarjeta


class ListadoMovimientosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empleado = User.objects.create_superuser('empleado')
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

    def setUp(self):
        self.client.force_login(self.empleado)

    def test_listado_ordenado_con_fecha_e_importe(self):
        respuesta = self.client.get(reverse('lista_movimientos'))

        self.assertQuerySetEqual(
            respuesta.context['movimientos_listado'],
            [self.gasto_posterior, self.gasto_final, self.ingreso, self.gasto_inicial],
        )
        self.assertContains(respuesta, '30/11/2026')
        self.assertContains(respuesta, '22,50 €')

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
        cls.empleado = User.objects.create_superuser('empleado')
        cls.cliente = Cliente.objects.create(nombre='César Manuel', apellidos='Prueba', email='cesar@example.test')
        cls.cuenta = Cuenta.objects.create(cliente=cls.cliente, iban='ES000002', saldo=Decimal('100'))
        cls.ahorro = Cuenta.objects.create(cliente=cls.cliente, iban='ES000003', saldo=Decimal('300'))

    def setUp(self):
        self.client.force_login(self.empleado)

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
        self.assertContains(ingreso, '150,00 €')
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
        self.assertContains(cliente, 'Saldo total: 430,00 €')

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


class VistasBasadasEnClasesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empleado = User.objects.create_superuser('empleado')
        cls.cliente = Cliente.objects.create(nombre='Ana', apellidos='Pérez', email='ana@example.test')
        cls.cuenta = Cuenta.objects.create(cliente=cls.cliente, iban='ES000010', saldo=Decimal('25'))
        cls.tarjeta = Tarjeta.objects.create(
            cuenta=cls.cuenta, numero='4111111111111111', fecha_caducidad=date(2027, 1, 1),
        )

    def setUp(self):
        self.client.force_login(self.empleado)

    def test_listado_y_detalle_de_clientes(self):
        listado = self.client.get(reverse('lista_clientes'))

        self.assertQuerySetEqual(listado.context['clientes_listado'], [self.cliente])
        self.assertContains(listado, 'Ana Pérez')

        detalle = self.client.get(reverse('detalle_cliente', args=[self.cliente.pk]))
        self.assertEqual(detalle.context['cliente'].saldo_total, Decimal('25'))
        self.assertContains(detalle, 'Saldo total: 25,00 €')

    def test_listado_y_detalle_de_tarjetas(self):
        listado = self.client.get(reverse('lista_tarjetas'))

        self.assertQuerySetEqual(listado.context['tarjetas_listado'], [self.tarjeta])
        self.assertContains(listado, 'ES000010')

        detalle = self.client.get(reverse('detalle_tarjeta', args=[self.tarjeta.pk]))
        self.assertEqual(detalle.context['tarjeta'], self.tarjeta)
        self.assertContains(detalle, '4111111111111111')


class RolesAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cliente = Cliente.objects.create(nombre='Ana', apellidos='Pérez', email='ana@example.test')
        cuenta = Cuenta.objects.create(cliente=cliente, iban='ES000011')
        cls.movimiento = Movimiento.objects.create(
            cuenta=cuenta, concepto='Cine', tipo='gasto', importe=Decimal('9.50'), fecha=date(2026, 11, 1),
        )
        cls.consulta = User.objects.create_user('consulta', password='clave', is_staff=True)
        cls.consulta.groups.add(Group.objects.get(name='Consulta de movimientos'))
        cls.editor = User.objects.create_user('editor', password='clave', is_staff=True)
        cls.editor.groups.add(Group.objects.get(name='Edición de movimientos'))

    def test_consulta_solo_puede_ver_los_movimientos(self):
        self.client.force_login(self.consulta)

        listado = self.client.get(reverse('admin:appBanco_movimiento_changelist'))
        self.assertEqual(listado.status_code, 200)
        self.assertNotContains(listado, reverse('admin:appBanco_movimiento_add'))

        añadir = self.client.get(reverse('admin:appBanco_movimiento_add'))
        self.assertEqual(añadir.status_code, 403)

        cambiar = self.client.post(
            reverse('admin:appBanco_movimiento_change', args=[self.movimiento.pk]),
            {'concepto': 'Cine', 'tipo': 'gasto', 'importe': '9.50', 'fecha': '2026-11-01'},
        )
        self.assertEqual(cambiar.status_code, 403)

    def test_editor_puede_cambiar_los_movimientos(self):
        self.client.force_login(self.editor)

        listado = self.client.get(reverse('admin:appBanco_movimiento_changelist'))
        self.assertContains(listado, reverse('admin:appBanco_movimiento_add'))

        añadir = self.client.get(reverse('admin:appBanco_movimiento_add'))
        self.assertEqual(añadir.status_code, 200)


class AccesoYAltaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        titular = Cliente.objects.create(nombre='Otro', apellidos='Cliente', email='otro@example.test')
        cls.otra_cuenta = Cuenta.objects.create(cliente=titular, iban='DEMOAJENA')
        Movimiento.objects.create(
            cuenta=cls.otra_cuenta, concepto='Movimiento ajeno', importe=Decimal('35'), fecha=date(2026, 11, 26),
        )

    def datos_alta(self):
        return {
            'username': 'cliente_demo', 'first_name': 'Sam', 'last_name': 'Demo',
            'email': 'Sam@EXAMPLE.test', 'telefono': '', 'tipo_cuenta': 'ahorro',
            'password1': 'Brisa!remota73', 'password2': 'Brisa!remota73',
        }

    def test_visitantes_solo_ven_las_paginas_publicas(self):
        for nombre in ('principal', 'sobre', 'contacto', 'alta_cliente'):
            self.assertEqual(self.client.get(reverse(nombre)).status_code, 200)
        inicio = self.client.get(reverse('principal'))
        for nombre in ('lista_clientes', 'lista_cuentas', 'lista_tarjetas', 'lista_movimientos'):
            ruta = reverse(nombre)
            with self.subTest(ruta=ruta):
                self.assertNotContains(inicio, f'href="{ruta}"')
                self.assertRedirects(self.client.get(ruta), f"{reverse('login')}?next={ruta}")
        ruta_cuenta = reverse('detalle_cuenta', args=[self.otra_cuenta.pk])
        self.assertEqual(self.client.post(ruta_cuenta).status_code, 302)

    def test_alta_crea_una_cuenta_propia_y_no_da_permisos_de_empleado(self):
        respuesta = self.client.post(reverse('alta_cliente'), self.datos_alta(), follow=True)
        self.assertRedirects(respuesta, reverse('mi_cuenta'))
        usuario = User.objects.get(username='cliente_demo')
        self.assertTrue(usuario.check_password(self.datos_alta()['password1']))
        self.assertFalse(usuario.is_staff)
        self.assertEqual(usuario.cliente.email, 'sam@example.test')
        cuenta = usuario.cliente.cuentas.get()
        self.assertEqual(cuenta.tipo, 'ahorro')
        self.assertEqual(cuenta.saldo, Decimal('0'))
        self.assertContains(respuesta, cuenta.iban)
        self.assertNotContains(respuesta, self.otra_cuenta.iban)
        self.assertNotContains(respuesta, 'Movimiento ajeno')
        Movimiento.objects.create(
            cuenta=cuenta, concepto='Ingreso propio', importe=Decimal('20'), fecha=date(2026, 11, 26),
        )
        personal = self.client.get(reverse('mi_cuenta'))
        self.assertContains(personal, 'Ingreso propio')
        self.assertNotContains(personal, 'Movimiento ajeno')
        detalle = reverse('detalle_cuenta', args=[self.otra_cuenta.pk])
        self.assertEqual(self.client.get(detalle).status_code, 403)
        self.assertEqual(self.client.post(detalle).status_code, 403)

        self.client.logout()
        sesion = self.client.post(reverse('login'), {
            'username': usuario.username, 'password': self.datos_alta()['password1'],
        })
        self.assertRedirects(sesion, reverse('mi_cuenta'))

    def test_el_correo_existente_no_vincula_una_cuenta_ajena(self):
        datos = {**self.datos_alta(), 'email': 'OTRO@example.test'}
        respuesta = self.client.post(reverse('alta_cliente'), datos)
        self.assertContains(respuesta, 'Ya hay un cliente registrado con este correo electrónico.')
        self.assertFalse(User.objects.filter(username=datos['username']).exists())
        self.assertIsNone(Cliente.objects.get(email='otro@example.test').usuario)

    def test_empleado_con_permiso_de_consulta_no_puede_registrar_movimientos(self):
        empleado = User.objects.create_user('consulta_cuentas', is_staff=True)
        permiso = Permission.objects.get(content_type__app_label='appBanco', codename='view_cuenta')
        empleado.user_permissions.add(permiso)
        self.client.force_login(empleado)

        ruta = reverse('detalle_cuenta', args=[self.otra_cuenta.pk])
        self.assertNotContains(self.client.get(ruta), 'Añadir movimiento')
        self.assertNotContains(self.client.get(ruta), 'Movimiento ajeno')
        self.assertEqual(self.client.post(ruta).status_code, 403)
