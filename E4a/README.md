# DeustoBanco

Proyecto web colaborativo de Ingeniería Web (2026-27): gestión bancaria con Django.

## Puesta en marcha

Desde esta carpeta (`E4a/`):

```bash
python -m venv ing_web
source ing_web/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata datos_ensayo
python manage.py createsuperuser
python manage.py runserver
```

`datos_ensayo` es el juego de ensayo con clientes, cuentas, tarjetas y movimientos.

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
