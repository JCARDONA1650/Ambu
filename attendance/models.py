# attendance/models.py
from decimal import Decimal
from datetime import timedelta
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import secrets
import uuid  # ← para client_uuid en AttendanceScan

User = get_user_model()


# ──────────────────────────────────────────────────────────────────────────────
# Proyectos / Empleados / Asistencia
# ──────────────────────────────────────────────────────────────────────────────

class Project(models.Model):
    name = models.CharField("Proyecto", max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    supervisors = models.ManyToManyField(User, related_name="supervised_projects", blank=True)
    employees = models.ManyToManyField("Employee", related_name="projects", blank=True)

    # Valor marco del contrato (ingreso objetivo/base del proyecto)
    contract_value = models.DecimalField(
        "Valor del contrato (USD)",
        max_digits=12, decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    qr_secret = models.CharField(max_length=64, default=secrets.token_urlsafe, editable=False)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    # Helpers de finanzas (mes a mes filtrarás en la vista)
    def total_income(self):
        return sum((i.amount for i in self.incomes.all()), start=Decimal("0.00"))

    def total_expense(self):
        return sum((e.amount for e in self.expenses.all()), start=Decimal("0.00"))


class Employee(models.Model):
    full_name = models.CharField("Nombre completo", max_length=150)
    position = models.CharField("Cargo", max_length=100, blank=True)
    hourly_rate = models.DecimalField(
        "Tarifa por hora (USD)",
        max_digits=7, decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


def evidence_upload_path(instance, filename):
    emp_slug = slugify(instance.employee.full_name) or "empleado"
    return f"attendance/{instance.project.slug}/{emp_slug}/{instance.date:%Y/%m/%d}/{filename}"


class Attendance(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT, verbose_name="Proyecto")
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, verbose_name="Empleado")
    date = models.DateField("Fecha", default=timezone.localdate)
    check_in = models.DateTimeField("Hora ingreso", blank=True, null=True)
    check_out = models.DateTimeField("Hora salida", blank=True, null=True)
    evidence_photo = models.ImageField("Foto constancia", upload_to=evidence_upload_path, blank=True, null=True)
    notes = models.CharField("Observaciones", max_length=200, blank=True)

    # 🔸 Override manual (opcional) para minutos netos ya “cerrados”
    manual_minutes = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Override de minutos netos (ya con reglas aplicadas)."
    )
    manual_note = models.CharField("Motivo ajuste", max_length=200, blank=True)

    class Meta:
        unique_together = ("project", "employee", "date")
        ordering = ["-date", "project__name", "employee__full_name"]

    def worked_minutes(self) -> int:
        """
        Minutos trabajados NETOS con redondeo al múltiplo de 30 más cercano:
        - Si hay override (manual_minutes) se usa ese valor.
        - Si es sábado (weekday==5): NO se descuenta almuerzo.
        - Otros días: si el bruto > 5h, se descuenta 1h de almuerzo.
        - Luego se redondea al múltiplo de 30 más cercano.
          Ej.: 7:01→7:00, 7:20→7:30, 7:38→7:30, 7:40→8:00.
        """
        if self.manual_minutes is not None:
            return int(self.manual_minutes)

        if self.check_in and self.check_out:
            delta = self.check_out - self.check_in
            gross = int(delta.total_seconds() // 60)  # minutos brutos

            # Día del registro
            att_date = self.date or timezone.localtime(self.check_in).date()
            is_saturday = (att_date.weekday() == 5) if att_date else False

            # Descuento 1h de almuerzo si NO es sábado y trabajó > 5h
            if not is_saturday and gross > 300:
                gross -= 60

            net = max(0, gross)

            # Redondeo al múltiplo de 30 más cercano
            remainder = net % 30
            if remainder < 15:
                net -= remainder  # hacia abajo
            else:
                net += (30 - remainder)  # hacia arriba

            return net

        return 0

    def worked_hhmm(self) -> str:
        m = self.worked_minutes()
        return f"{m//60:02d}:{m%60:02d}"

    def __str__(self):
        return f"{self.project} • {self.employee} • {self.date} ({self.worked_hhmm()})"


# ──────────────────────────────────────────────────────────────────────────────
# Escaneos idempotentes (para cola offline y reintentos sin duplicados)
# ──────────────────────────────────────────────────────────────────────────────
class AttendanceScan(models.Model):
    """
    Registro liviano del ESCANEO (no del cálculo de horas).
    Permite reintentar cuando no hay red, sin duplicar:
    - client_uuid: único por escaneo (lo genera el front).
    - device_ts: hora en el dispositivo al momento del scan.
    """
    client_uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, on_delete=models.PROTECT, null=True, blank=True)
    action = models.CharField(max_length=10, choices=[("in", "in"), ("out", "out")])
    device_ts = models.DateTimeField()
    server_ts = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=20, default="qr")

    class Meta:
        indexes = [
            models.Index(fields=["employee", "server_ts"]),
        ]
        ordering = ["-server_ts"]

    def __str__(self):
        return f"{self.employee} • {self.action} • {self.device_ts:%Y-%m-%d %H:%M} ({self.client_uuid})"


# ──────────────────────────────────────────────────────────────────────────────
# Nómina (periodos y líneas)
# ──────────────────────────────────────────────────────────────────────────────

class PayrollPeriod(models.Model):
    PERIOD_STATUS = (
        ("OPEN", "Abierta"),
        ("CLOSED", "Cerrada"),
    )
    start_date = models.DateField("Inicio")
    end_date = models.DateField("Fin")
    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, null=True, blank=True,
        verbose_name="Proyecto (opcional)"
    )
    status = models.CharField(max_length=10, choices=PERIOD_STATUS, default="OPEN")

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    # Opcional: quién/cuándo cerró (histórico más fuerte)
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.PROTECT, related_name="closed_payroll_periods"
    )

    class Meta:
        ordering = ["-start_date"]
        unique_together = ("start_date", "end_date", "project")

    def __str__(self):
        scope = self.project.name if self.project else "Todos los proyectos"
        return f"{self.start_date} → {self.end_date} • {scope} • {self.status}"

    @property
    def is_open(self):
        return self.status == "OPEN"


class PayrollLine(models.Model):
    period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, related_name="lines")
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)

    minutes = models.PositiveIntegerField(default=0)  # acumulado en el periodo
    hourly_rate = models.DecimalField(
        max_digits=7, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    base_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    adjustment = models.DecimalField("Ajuste (+/-)", max_digits=10, decimal_places=2, default=Decimal("0.00"))
    notes = models.CharField("Notas ajuste", max_length=200, blank=True)

    class Meta:
        unique_together = ("period", "employee")
        ordering = ["employee__full_name"]

    @property
    def hours_hhmm(self):
        return f"{self.minutes//60:02d}:{self.minutes%60:02d}"

    @property
    def total(self):
        return (self.base_amount + self.adjustment).quantize(Decimal("0.01"))

    def __str__(self):
        return f"{self.period} • {self.employee} • {self.hours_hhmm} → ${self.total}"


# ──────────────────────────────────────────────────────────────────────────────
# Finanzas del proyecto (ingresos y gastos)
# ──────────────────────────────────────────────────────────────────────────────

class ProjectIncome(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="incomes")
    date = models.DateField()
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    description = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"[{self.project}] {self.date} • +${self.amount} • {self.description or 'Ingreso'}"


class ProjectExpense(models.Model):
    CATEGORY = [
        ("materials", "Materiales"),
        ("transport", "Transporte"),
        ("meals", "Comida"),
        ("tools", "Herramientas"),
        ("other", "Otros"),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="expenses")
    date = models.DateField()
    category = models.CharField(max_length=20, choices=CATEGORY, default="other")
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    description = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"[{self.project}] {self.date} • {self.get_category_display()} • -${self.amount}"
