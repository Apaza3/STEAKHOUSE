from django import forms
from .models import Reserva, Mesa

class ReservaForm(forms.ModelForm):
    
    # --- ¡NUEVO! Opciones de Duración ---
    DURACION_CHOICES = (
        (1, '1 Hora'),
        (2, '2 Horas (Estándar)'),
        (3, '3 Horas'),
        (4, '4 Horas'),
    )

    # --- ¡NUEVO! Campo de Duración ---
    duracion_horas = forms.ChoiceField(
        choices=DURACION_CHOICES,
        initial=2, # Por defecto 2 horas
        label="¿Cuánto tiempo te quedas?",
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'})
    )

    class Meta:
        model = Reserva
        fields = [
            'fecha_reserva',
            'hora_reserva',
            'duracion_horas', # <-- ¡Añadido!
            'numero_personas',
            'tipo_pago',
            'cliente', # ¡Lo mantenemos aquí para que el form lo valide!
        ]
        # ¡HEMOS QUITADO EL CAMPO 'mesa'!
        widgets = {
            'fecha_reserva': forms.DateInput(attrs={'class': 'form-control form-control-lg', 'type': 'date'}),
            'hora_reserva': forms.TimeInput(attrs={'class': 'form-control form-control-lg', 'type': 'time'}),
            'numero_personas': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'min': '1'}),
            'tipo_pago': forms.Select(attrs={'class': 'form-select form-select-lg', 'id': 'id_tipo_pago'}),
            
            # Hacemos que el campo 'cliente' sea invisible.
            'cliente': forms.HiddenInput(),
        }
        labels = {
            'fecha_reserva': 'Fecha de Reserva',
            'hora_reserva': 'Hora de Reserva',
            'numero_personas': 'Número de Personas',
            'tipo_pago': 'Tipo de Reserva',
        }

    # ¡El __init__ ya no necesita el campo 'mesa'!
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)