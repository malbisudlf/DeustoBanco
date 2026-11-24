from django.core.exceptions import ValidationError
from django.db import models, router, transaction
from django.db.models import F
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# Create your models here.
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    fecha_alta = models.DateField(auto_now_add=True)

    class Meta: 
        verbose_name = "Cliente" 
        verbose_name_plural = "Clientes" 


    def __str__(self):
        return f"{self.nombre} {self.apellidos}"


class Cuenta(models.Model):
    TIPOS_CUENTA = [
        ("corriente", "Corriente"),
        ("ahorro", "Ahorro"),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="cuentas")
    iban = models.CharField(max_length=34, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPOS_CUENTA, default="corriente")
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fecha_apertura = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Cuenta"
        verbose_name_plural = "Cuentas"


    def __str__(self):
        return f"{self.iban} ({self.cliente})"


class Tarjeta(models.Model):
    TIPOS_TARJETA = [
        ("debito", "Débito"),
        ("credito", "Crédito"),
    ]

    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE, related_name="tarjetas")
    numero = models.CharField(max_length=16, unique=True)
    tipo = models.CharField(max_length=10, choices=TIPOS_TARJETA, default="debito")
    fecha_caducidad = models.DateField()
    activa = models.BooleanField(default=True)
    limite_diario = models.DecimalField(max_digits=8, decimal_places=2, default=600)

    class Meta:
        verbose_name = "Tarjeta"
        verbose_name_plural = "Tarjetas"


    def __str__(self):
        return f"{self.numero} ({self.get_tipo_display()})"


class Movimiento(models.Model):
    TIPOS_MOVIMIENTO = [
        ("ingreso", "Ingreso"),
        ("gasto", "Gasto"),
    ]

    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE, related_name="movimientos")
    concepto = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPOS_MOVIMIENTO, default="ingreso")
    importe = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField()

    class Meta:
        verbose_name = "Movimiento"
        verbose_name_plural = "Movimientos"

    def clean(self):
        super().clean()
        if self.importe is not None and self.importe <= 0:
            raise ValidationError({'importe': 'Introduce un importe mayor que cero.'})

    @property
    def variacion_saldo(self):
        return -self.importe if self.tipo == 'gasto' else self.importe

    def save(self, *, force_insert=False, force_update=False, using=None, update_fields=None):
        if update_fields is not None:
            update_fields = frozenset(update_fields)
            if not update_fields:
                return

        using = using or router.db_for_write(type(self), instance=self)
        movimientos = type(self).objects.using(using)
        with transaction.atomic(using=using):
            anterior = None
            if self.pk is not None and not force_insert:
                anterior = movimientos.select_for_update().filter(pk=self.pk).first()

            super().save(
                force_insert=force_insert, force_update=force_update,
                using=using, update_fields=update_fields,
            )
            guardado = movimientos.get(pk=self.pk)
            variaciones = {guardado.cuenta_id: guardado.variacion_saldo}
            if anterior is not None:
                variaciones[anterior.cuenta_id] = (
                    variaciones.get(anterior.cuenta_id, 0) - anterior.variacion_saldo
                )

            for cuenta_id, variacion in sorted(variaciones.items()):
                if variacion:
                    Cuenta.objects.using(using).filter(pk=cuenta_id).update(saldo=F('saldo') + variacion)

    def __str__(self):
        return f"{self.concepto} ({self.get_tipo_display()})"


@receiver(pre_delete, sender=Movimiento)
def revertir_saldo_al_borrar_movimiento(sender, instance, using, **kwargs):
    movimiento = sender.objects.using(using).select_for_update().filter(pk=instance.pk).first()
    if movimiento is not None:
        Cuenta.objects.using(using).filter(pk=movimiento.cuenta_id).update(
            saldo=F('saldo') - movimiento.variacion_saldo,
        )
