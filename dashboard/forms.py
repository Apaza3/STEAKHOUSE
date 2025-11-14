from django import forms
from core.models import Mesa # Importamos el modelo Mesa desde 'core'

class MesaForm(forms.ModelForm):
    """
    Formulario para Crear y Editar Mesas en el panel de admin.
    """
    class Meta:
        model = Mesa
        # Incluimos todos los campos que el admin debe gestionar
        fields = ['numero', 'capacidad', 'tipo', 'estado']
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'numero': 'Número de Mesa',
            'capacidad': 'Capacidad (personas)',
            'tipo': 'Tipo de Mesa',
            'estado': 'Estado Actual',
        }