from django import forms
from django.contrib.auth.models import User
from .models import Cliente

class ClienteRegistrationForm(forms.ModelForm):
    """
    Formulario para registrar un nuevo Cliente.
    Pide campos del modelo User y del modelo Cliente.
    """
    # Campos para el modelo User
    username = forms.CharField(
        label='Nombre de Usuario', 
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'})
    )
    password = forms.CharField(
        label='Contraseña', 
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})
    )
    password_confirm = forms.CharField(
        label='Confirmar Contraseña', 
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})
    )

    class Meta:
        model = Cliente  # Basado en el modelo Cliente
        fields = ['nombre', 'apellido', 'email', 'telefono'] # Campos del modelo Cliente
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-lg'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Opcional'}),
        }

    def clean_username(self):
        """Valida que el nombre de usuario no exista."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso. Por favor, elige otro.")
        return username

    def clean_email(self):
        """Valida que el email no exista."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists() or Cliente.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email ya está registrado. Por favor, usa otro.")
        return email

    def clean_password_confirm(self):
        """Valida que las contraseñas coincidan."""
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password_confirm

    def save(self, commit=True):
        """
        Guarda el nuevo User y el nuevo Cliente.
        """
        # 1. Crear el User
        user = User.objects.create_user(
            username=self.cleaned_data.get('username'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('password')
        )
        
        # 2. Crear el Cliente (sin guardar)
        cliente = super().save(commit=False)
        
        # 3. Enlazar el User al Cliente
        cliente.usuario = user
        
        if commit:
            cliente.save()
            
        return cliente