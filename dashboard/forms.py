from django import forms
from core.models import Mesa
from django.contrib.auth.models import User, Group # <-- ¡Importación añadida!
from clientes.models import Cliente
from django.db import transaction

class MesaForm(forms.ModelForm):
    """
    Formulario para Crear y Editar Mesas en el panel de admin.
    """
    class Meta:
        model = Mesa
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

# ===================================================
# FORMULARIO PARA CREAR EMPLEADOS (STAFF) - ACTUALIZADO
# ===================================================
class EmpleadoCreateForm(forms.Form):
    """
    Formulario para que un Admin cree una nueva cuenta de Empleado (staff).
    """
    # Campos para el modelo User
    username = forms.CharField(label='Nombre de Usuario', max_length=100)
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    
    # Campos para el modelo Cliente
    nombre = forms.CharField(label='Nombre', max_length=100)
    apellido = forms.CharField(label='Apellido', max_length=100)
    telefono = forms.CharField(label='Teléfono', max_length=20, required=False)
    
    # --- ¡CAMPO NUEVO! ---
    # Filtramos para que solo muestre los grupos que creaste
    rol = forms.ModelChoiceField(
        queryset=Group.objects.filter(name__in=['Cajero', 'Mesero']),
        label="Rol del Empleado",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    # ----------------------
    
    # Aplicamos la clase 'form-control' a todos los campos de texto
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})
        self.fields['apellido'].widget.attrs.update({'class': 'form-control'})
        self.fields['telefono'].widget.attrs.update({'class': 'form-control'})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists() or Cliente.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email ya está registrado.")
        return email

    @transaction.atomic # Asegura que todo se guarde o nada se guarde
    def save(self):
        # 1. Crear el User
        user = User.objects.create_user(
            username=self.cleaned_data.get('username'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('password')
        )
        
        # ¡IMPORTANTE! Marcamos esta cuenta como Empleado
        user.is_staff = True
        user.save()
        
        # --- ¡CAMBIO! Asignamos el rol (Grupo) ---
        rol_seleccionado = self.cleaned_data.get('rol')
        user.groups.add(rol_seleccionado)
        # ----------------------------------------
        
        # 2. Crear el perfil Cliente enlazado
        cliente = Cliente.objects.create(
            usuario=user,
            nombre=self.cleaned_data.get('nombre'),
            apellido=self.cleaned_data.get('apellido'),
            email=self.cleaned_data.get('email'),
            telefono=self.cleaned_data.get('telefono')
        )
        return cliente