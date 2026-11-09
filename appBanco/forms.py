from django import forms
from .models import Movimiento


class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = ['concepto', 'tipo', 'importe', 'fecha']
