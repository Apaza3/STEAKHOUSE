from django import forms
from .models import Reserva
from datetime import datetime # <--- ¡ESTA LÍNEA FALTABA!

class ReservaForm(forms.ModelForm):
    
    DURACION_CHOICES = (
        (2, '2 Horas (Estándar)'),
        (3, '3 Horas (+50 Bs)'),
        (4, '4 Horas (+100 Bs)'),
    )

    duracion_horas = forms.ChoiceField(
        choices=DURACION_CHOICES,
        initial=2,
        label="Duración",
        widget=forms.Select(attrs={'class': 'form-select', 'onchange': 'cargarMesas()'})
    )

    # Campo oculto para guardar el ID de la mesa que el usuario toque en el mapa
    mesa_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Reserva
        fields = [
            'fecha_reserva',
            'hora_reserva',
            'duracion_horas',
            'numero_personas',
            'tipo_pago',
            'cliente',
        ]
        widgets = {
            'fecha_reserva': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date', 
                'onchange': 'cargarMesas()',
                'min': datetime.now().date().isoformat() # Evita fechas pasadas
            }),
            'hora_reserva': forms.TimeInput(attrs={
                'class': 'form-control', 
                'type': 'time', 
                'onchange': 'cargarMesas()',
                'min': '12:00', 'max': '23:00' # Restricción visual
            }),
            'numero_personas': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': '1', 
                'onchange': 'filtrarMesasPorCapacidad()'
            }),
            'tipo_pago': forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo_pago'}),
            'cliente': forms.HiddenInput(),
        }
        labels = {
            'fecha_reserva': 'Fecha',
            'hora_reserva': 'Hora',
            'numero_personas': 'Personas',
            'tipo_pago': 'Método de Pago',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Validaciones extra si es necesario