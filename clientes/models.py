from django.db import models

# Reemplaza 'CREATE TABLE Clientes_Tipo'
class ClientesTipo(models.Model):
    tipo_cliente = models.CharField(max_length=50)

    def __str__(self):
        return self.tipo_cliente

# Reemplaza 'CREATE TABLE Clientes'
class Cliente(models.Model):
    cliente_tipo = models.ForeignKey(ClientesTipo, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_cliente = models.CharField(max_length=100)
    email_cliente = models.EmailField(max_length=100, unique=True)
    telefono_cliente = models.CharField(max_length=50, blank=True, null=True)
    fecha_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nombre_cliente

# Reemplaza 'CREATE TABLE Clientes_Dispositivos'
class ClientesDispositivos(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    num_dispos = models.CharField(max_length=50, help_text="ID de dispositivo para notificaciones")

    def __str__(self):
        return f"Dispositivo de {self.cliente.nombre_cliente}"