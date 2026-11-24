from django.apps import apps as global_apps
from django.conf import settings
from django.contrib.auth.management import create_permissions
from django.db import migrations

# Cada rol es un grupo del panel de administración con los permisos de Movimiento indicados.
ROLES = {
    'Consulta de movimientos': [
        'view_movimiento',
    ],
    'Edición de movimientos': [
        'view_movimiento',
        'add_movimiento',
        'change_movimiento',
        'delete_movimiento',
    ],
}


def crear_roles(apps, schema_editor):
    # En una base de datos nueva los permisos de la app todavía no existe al ejecutar
    # esta migración, así que se crean antes de asignarlos a los grupos.
    for app_config in global_apps.get_app_configs():
        if app_config.name == 'appBanco':
            create_permissions(app_config, apps=apps, using=schema_editor.connection.alias)

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    grupos = Group.objects.using(schema_editor.connection.alias)
    permisos = Permission.objects.using(schema_editor.connection.alias)
    for nombre, codenames in ROLES.items():
        grupo, _ = grupos.get_or_create(name=nombre)
        grupo.permissions.set(
            permisos.filter(content_type__app_label='appBanco', codename__in=codenames),
        )


def borrar_roles(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.using(schema_editor.connection.alias).filter(name__in=ROLES).delete()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appBanco', '0005_alter_movimiento_fecha'),
    ]

    operations = [
        migrations.RunPython(crear_roles, borrar_roles),
    ]
