from django import forms
from .models import Movimiento


class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = ['concepto', 'tipo', 'importe', 'fecha']


class FiltroMovimientosForm(forms.Form):
    tipo = forms.ChoiceField(
        label='Tipo de movimiento',
        required=False,
        choices=[('', 'Todos'), *Movimiento.TIPOS_MOVIMIENTO],
        error_messages={'invalid_choice': 'Selecciona un tipo de movimiento válido.'},
    )
    desde = forms.DateField(
        label='Desde',
        required=False,
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        error_messages={'invalid': 'Introduce una fecha de inicio válida.'},
    )
    hasta = forms.DateField(
        label='Hasta',
        required=False,
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        error_messages={'invalid': 'Introduce una fecha de fin válida.'},
    )

    def clean(self):
        datos = super().clean()
        desde, hasta = datos.get('desde'), datos.get('hasta')
        if desde and hasta and desde > hasta:
            self.add_error('hasta', 'La fecha «Hasta» debe ser igual o posterior a «Desde».')
        return datos
