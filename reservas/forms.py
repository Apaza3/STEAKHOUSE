from django import forms
from .models import Reserva
from core.models import Mesa
from clientes.models import Cliente

class ReservaForm(forms.ModelForm):
    # Hacemos que la fecha y hora sean 'Inputs' de HTML5
    fecha_reserva = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-lg'})
    )
    hora_reserva = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control form-control-lg'})
    )

    class Meta:
        model = Reserva
        fields = [
            'cliente', 
            'mesa', 
            'fecha_reserva', 
            'hora_reserva', 
            'numero_personas', 
            'tipo_pago'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplicamos clases de Bootstrap a todos los campos
        self.fields['cliente'].widget.attrs.update({'class': 'form-select form-select-lg'})
        self.fields['mesa'].widget.attrs.update({'class': 'form-select form-select-lg'})
        self.fields['numero_personas'].widget.attrs.update({'class': 'form-control form-control-lg'})
        self.fields['tipo_pago'].widget.attrs.update({'class': 'form-select form-select-lg'})
        
        # Hacemos que la mesa sea opcional en el formulario
        self.fields['mesa'].required = False
        
        # Filtramos para mostrar solo mesas disponibles
        self.fields['mesa'].queryset = Mesa.objects.filter(estado='DISPONIBLE')