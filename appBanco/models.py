from django.db import models

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
