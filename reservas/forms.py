from django import forms
from .models import Reserva, Mesa

class ReservaForm(forms.ModelForm):
    
    class Meta:
        model = Reserva
        fields = [
            'fecha_reserva',
            'hora_reserva',
            'numero_personas',
            'mesa',
            'tipo_pago',
            'cliente', # ¡Lo mantenemos aquí para que el form lo valide!
        ]
        widgets = {
            'fecha_reserva': forms.DateInput(attrs={'class': 'form-control form-control-lg', 'type': 'date'}),
            'hora_reserva': forms.TimeInput(attrs={'class': 'form-control form-control-lg', 'type': 'time'}),
            'numero_personas': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'min': '1'}),
            'mesa': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'tipo_pago': forms.Select(attrs={'class': 'form-select form-select-lg', 'id': 'id_tipo_pago'}),
            
            # --- ¡AQUÍ ESTÁ EL CAMBIO! ---
            # Hacemos que el campo 'cliente' sea invisible.
            # La vista se encargará de rellenarlo.
            'cliente': forms.HiddenInput(),
            # --- FIN DEL CAMBIO ---
        }
        labels = {
            'fecha_reserva': 'Fecha de Reserva',
            'hora_reserva': 'Hora de Reserva',
            'numero_personas': 'Número de Personas',
            'mesa': 'Mesa (Opcional)',
            'tipo_pago': 'Tipo de Reserva',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacemos que el campo 'mesa' no sea obligatorio
        self.fields['mesa'].required = False
        # El queryset de 'mesa' se actualizará en la vista
        self.fields['mesa'].queryset = Mesa.objects.none()