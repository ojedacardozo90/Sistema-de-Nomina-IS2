# ============================================================
# auditlog_context.py — Contexto de request (Thread Local)
# ------------------------------------------------------------
# Permite que las señales accedan al usuario, IP y User-Agent
# sin romper la arquitectura REST ni depender del middleware.
# ============================================================

import threading

_local = threading.local()

def set_request(request):
    """Guarda el objeto request actual en una variable local por hilo."""
    _local.request = request

def get_request():
    """Obtiene el request actual (si existe)."""
    return getattr(_local, "request", None)
