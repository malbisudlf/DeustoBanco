from uuid import uuid4

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.utils import timezone

from .models import Cliente, Cuenta, Movimiento


class AltaClienteForm(UserCreationForm):
    first_name = forms.CharField(
        label='Nombre', max_length=100, widget=forms.TextInput(attrs={'autocomplete': 'given-name'}),
    )
    last_name = forms.CharField(
        label='Apellidos', max_length=150, widget=forms.TextInput(attrs={'autocomplete': 'family-name'}),
    )
    email = forms.EmailField(
        label='Correo electrónico', widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
    )
    telefono = forms.CharField(
        label='Teléfono (opcional)', required=False, max_length=20,
        widget=forms.TextInput(attrs={'type': 'tel', 'autocomplete': 'tel'}),
    )
    tipo_cuenta = forms.ChoiceField(label='Tipo de cuenta', choices=Cuenta.TIPOS_CUENTA)
    field_order = ('first_name', 'last_name', 'email', 'telefono', 'tipo_cuenta', 'username', 'password1', 'password2')

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if Cliente.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya hay un cliente registrado con este correo electrónico.')
        return email

    @transaction.atomic
    def crear_cliente(self):
        usuario = self.save()
        cliente = Cliente.objects.create(
            usuario=usuario, nombre=usuario.first_name, apellidos=usuario.last_name,
            email=usuario.email, telefono=self.cleaned_data['telefono'],
        )
        Cuenta.objects.create(
            cliente=cliente, tipo=self.cleaned_data['tipo_cuenta'], iban=f'DEMO{uuid4().hex[:24].upper()}',
        )
        return usuario


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
