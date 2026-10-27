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