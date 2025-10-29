# ============================================================
# Señales de la app Nómina (envío automático de recibos)
# ============================================================

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Liquidacion

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Liquidacion)
def auto_enviar_recibo_al_cerrar(sender, instance: Liquidacion, created, **kwargs):
    """
    Si la liquidación está cerrada y aún no se envió el recibo,
    dispara el envío automático por email.
    """
    try:
        if instance.cerrada and not instance.enviado_email:
            # Import local para evitar import circular
            from .utils_email import enviar_recibo_email
            ok = enviar_recibo_email(instance)
            if ok:
                logger.info(
                    f"[Nómina] Recibo enviado automáticamente: "
                    f"{instance.empleado} - {instance.mes}/{instance.anio}"
                )
            else:
                logger.error(
                    f"[Nómina] Falló el envío automático del recibo: "
                    f"{instance.empleado} - {instance.mes}/{instance.anio}"
                )
    except Exception as e:
        logger.exception(f"[Nómina] Error en signal auto_enviar_recibo_al_cerrar: {e}")
