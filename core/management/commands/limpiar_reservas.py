from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from reservas.models import Reserva
from core.models import Mesa

class Command(BaseCommand):
    help = 'Limpia reservas pendientes no pagadas y marca las reservas como No-Show.'

    def handle(self, *args, **options):
        ahora = timezone.now()
        
        self.stdout.write(f"[{ahora.strftime('%Y-%m-%d %H:%M')}] Ejecutando script de limpieza de reservas...")

        # ===================================================
        # LÓGICA 1: CANCELAR RESERVAS PENDIENTES NO PAGADAS
        # (La idea que tú diste)
        # ===================================================
        
        # Límite: 15 minutos para pagar
        limite_pago = ahora - timedelta(minutes=15)
        
        # Buscamos reservas pendientes que se crearon hace más de 15 minutos
        reservas_pendientes = Reserva.objects.filter(
            estado='PENDIENTE',
            created_at__lt=limite_pago # created_at es el campo que añadimos antes
        )

        canceladas_pendientes = 0
        for reserva in reservas_pendientes:
            reserva.estado = 'CANCELADA'
            reserva.save()
            
            # ¡Liberamos la mesa!
            if reserva.mesa:
                reserva.mesa.estado = 'DISPONIBLE'
                reserva.mesa.save()
                
            canceladas_pendientes += 1

        if canceladas_pendientes > 0:
            self.stdout.write(self.style.WARNING(f'Se cancelaron {canceladas_pendientes} reservas PENDIENTES (pago no completado).'))
        else:
            self.stdout.write('No se encontraron reservas pendientes para limpiar.')

        # ===================================================
        # LÓGICA 2: MANEJAR "NO-SHOW"
        # (La regla del profesor)
        # ===================================================
        
        # Límite: 30 minutos de retraso
        limite_no_show_dt = ahora - timedelta(minutes=30)
        
        # Buscamos reservas CONFIRMADAS para HOY, cuya hora de inicio
        # sea ANTERIOR al límite de 30 minutos.
        reservas_no_show = Reserva.objects.filter(
            estado='CONFIRMADA',
            fecha_reserva=ahora.date(),
            hora_reserva__lt=limite_no_show_dt.time()
        )

        canceladas_no_show = 0
        for reserva in reservas_no_show:
            reserva.estado = 'NO_SHOW'
            reserva.save()
            
            # ¡Liberamos la mesa!
            if reserva.mesa:
                reserva.mesa.estado = 'DISPONIBLE'
                reserva.mesa.save()
            
            canceladas_no_show += 1

        if canceladas_no_show > 0:
            self.stdout.write(self.style.ERROR(f'Se marcaron {canceladas_no_show} reservas como NO-SHOW (retraso de 30 min).'))
        else:
            self.stdout.write('No se encontraron reservas para marcar como No-Show.')
            
        self.stdout.write(self.style.SUCCESS('Script de limpieza finalizado.'))