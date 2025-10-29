from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date, parse_datetime
from django.db.models import Q
from .models import AuditLog
from .serializers import AuditLogSerializer

class AuditLogViewSet(ReadOnlyModelViewSet):
    """
    GET /api/auditoria/logs/?modelo=Empleado&accion=update&usuario=3&desde=2025-01-01&hasta=2025-12-31&q=lucia
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AuditLogSerializer
    queryset = AuditLog.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        modelo = self.request.query_params.get("modelo")
        accion = self.request.query_params.get("accion")
        usuario = self.request.query_params.get("usuario")
        desde = self.request.query_params.get("desde")
        hasta = self.request.query_params.get("hasta")
        q = self.request.query_params.get("q")

        if modelo:
            qs = qs.filter(modelo__iexact=modelo)
        if accion:
            qs = qs.filter(accion=accion)
        if usuario:
            qs = qs.filter(usuario_id=usuario)
        if desde:
            qs = qs.filter(fecha__date__gte=parse_date(desde))
        if hasta:
            qs = qs.filter(fecha__date__lte=parse_date(hasta))
        if q:
            qs = qs.filter(
                Q(cambios__icontains=q)
                | Q(user_agent__icontains=q)
            )
        return qs.select_related("usuario")
