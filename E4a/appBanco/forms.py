from django import forms
from django.utils import timezone
from .models import Movimiento


class MovimientoForm(forms.ModelForm):
    fecha = forms.DateField(
        label='Fecha',
        initial=timezone.localdate,
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        error_messages={'required': 'Selecciona una fecha.', 'invalid': 'Selecciona una fecha válida.'},
    )

    class Meta:
        model = Movimiento
        fields = ['concepto', 'tipo', 'importe', 'fecha']
        help_texts = {'importe': 'Introduce el importe sin el símbolo €, por ejemplo 50.'}


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
