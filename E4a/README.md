# DeustoBanco

Proyecto web colaborativo de Ingeniería Web (2026-27): gestión bancaria con Django.

## Puesta en marcha

### Windows (PowerShell)

Si ya tienes el entorno `ing_web` en la raíz del repositorio, abre PowerShell desde esa raíz y ejecuta:

```powershell
cd E4a
..\ing_web\Scripts\python.exe manage.py migrate
..\ing_web\Scripts\python.exe manage.py runserver
```

Si es la primera vez que arrancas el proyecto, crea el entorno e instala las dependencias desde la raíz antes de ejecutar los comandos anteriores:

```powershell
py -3.12 -m venv ing_web
.\ing_web\Scripts\python.exe -m pip install -r E4a\requirements.txt
```

Con una base de datos vacía, puedes cargar los datos de ensayo después de `migrate` con `..\ing_web\Scripts\python.exe manage.py loaddata datos_ensayo` desde `E4a`.

### macOS y Linux

Desde la carpeta `E4a`:

```bash
python -m venv ing_web
source ing_web/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata datos_ensayo
python manage.py createsuperuser
python manage.py runserver
```

`datos_ensayo` es el juego de ensayo: 12 clientes, 21 cuentas, 17 tarjetas y 243 movimientos
(septiembre a noviembre de 2026), con los saldos coherentes con sus movimientos. Se puede cargar
varias veces sin duplicar datos.

El juego de ensayo incluye además un cliente de demostración para probar **Mi cuenta**:
usuario `amaia`, contraseña `amaia-demo-2026` (solo para pruebas en local).

## Acceso a la aplicación

- Los visitantes pueden consultar Inicio, El banco y Contacto. Desde **Hazte cliente** se puede abrir una cuenta de demostración con saldo inicial de 0 €.
- En **Mi cuenta**, el cliente registrado ve sus propias cuentas, tarjetas y movimientos recientes.
- Los empleados usan el mismo inicio de sesión. El panel muestra solo los apartados para los que tienen permiso. Un superusuario creado con `manage.py createsuperuser` puede probar todos los apartados.

## Roles del panel de administración

La migración `appBanco/migrations/0006_roles_movimientos.py` crea dos grupos:

| Grupo | Permisos sobre Movimiento |
|---|---|
| Consulta de movimientos | ver |
| Edición de movimientos | ver, añadir, cambiar y borrar |

Para probar los permisos con dos usuarios de prueba (`consulta` y `editor`, ambos con acceso al panel
de administración) se ejecuta:

```bash
python manage.py usuarios_roles --password <contraseña>
```

Los dos usuarios comparten la contraseña indicada en el comando.
