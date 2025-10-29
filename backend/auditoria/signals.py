from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.utils.module_loading import import_string
from django.conf import settings
 
from empleados.models import Empleado
from nomina_cal.models import Liquidacion, Concepto, DetalleLiquidacion
from nomina_cal.models_descuento import Descuento
from usuarios.models import Usuario
from .models import AuditLog
from .auditlog_context import get_request  # helper (debajo)


# ---- Helper para tener el request actual (thread-local) ----
# Guardalo como auditlog_context.py (mismo directorio "auditoria")
def _request_info():
    req = get_request()
    if not req:
        return None, None, None
    ip = req.META.get("REMOTE_ADDR")
    ua = req.META.get("HTTP_USER_AGENT", "")
    user = getattr(req, "user", None)
    if user and not user.is_authenticated:
        user = None
    return user, ip, ua

def _create_audit(instance, accion, before=None, after=None):
    user, ip, ua = _request_info()
    modelo = instance.__class__.__name__
    objeto_id = str(getattr(instance, "pk", None) or "")

    # cambios: si hay before/after hacemos diff simple
    cambios = {}
    try:
        if before is not None or after is not None:
            cambios = {"before": before or {}, "after": after or {}}
        else:
            cambios = {"snapshot": model_to_dict(instance)}
    except Exception:
        cambios = {}

    AuditLog.objects.create(
        modelo=modelo,
        objeto_id=objeto_id,
        accion=accion,
        usuario=user,
        cambios=cambios,
        ip=ip, user_agent=ua
    )

# ------- MODELOS A AUDITAR --------
AUDIT_MODELS = (Empleado, Liquidacion, Concepto, DetalleLiquidacion, Descuento, Usuario)

# Guardamos un snapshot pre_save para hacer diff
_pre_save_snapshots = {}

@receiver(pre_save)
def _capture_before(sender, instance, **kwargs):
    if sender not in AUDIT_MODELS:
        return
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            _pre_save_snapshots[(sender.__name__, instance.pk)] = model_to_dict(old)
        except sender.DoesNotExist:
            _pre_save_snapshots[(sender.__name__, instance.pk)] = {}

@receiver(post_save)
def _on_save(sender, instance, created, **kwargs):
    if sender not in AUDIT_MODELS:
        return
    key = (sender.__name__, instance.pk)
    before = _pre_save_snapshots.pop(key, {})
    after = {}
    try:
        after = model_to_dict(instance)
    except Exception:
        pass
    _create_audit(instance, "create" if created else "update", before=before if not created else {}, after=after)

@receiver(post_delete)
def _on_delete(sender, instance, **kwargs):
    if sender not in AUDIT_MODELS:
        return
    snap = {}
    try:
        snap = model_to_dict(instance)
    except Exception:
        pass
    _create_audit(instance, "delete", before=snap, after={})
