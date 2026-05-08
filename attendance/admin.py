# attendance/admin.py
from django.contrib import admin
from .models import (
    Project, Employee, Attendance,
    PayrollPeriod, PayrollLine,
    ProjectIncome, ProjectExpense
)

# ─── Proyectos ───────────────────────────────
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("supervisors", "employees")  # asignación fácil


# ─── Empleados ───────────────────────────────
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("full_name", "position", "hourly_rate", "active")
    list_filter = ("active",)
    search_fields = ("full_name", "position")


# ─── Asistencia ───────────────────────────────
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("project", "employee", "date", "check_in", "check_out", "worked_hhmm")
    list_filter = ("project", "date")
    search_fields = ("employee__full_name", "project__name")


# ─── Nómina ───────────────────────────────
class PayrollLineInline(admin.TabularInline):
    model = PayrollLine
    extra = 0
    can_delete = True  # ✅ permite eliminar líneas desde el inline
    readonly_fields = ("total", "hours_hhmm")  # dejamos calculados como solo lectura
    fields = ("employee", "minutes", "hours_hhmm", "hourly_rate",
              "base_amount", "adjustment", "notes", "total")


@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = ("start_date", "end_date", "project", "status", "created_by", "created_at")
    list_filter = ("status", "project")
    inlines = [PayrollLineInline]

    # ✅ permitir eliminar periodos desde admin
    def has_delete_permission(self, request, obj=None):
        return True

# ─── Ingresos y Gastos ───────────────────────────────
@admin.register(ProjectIncome)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ("project", "date", "description", "amount")
    list_filter = ("project", "date")
    search_fields = ("description", "project__name")


@admin.register(ProjectExpense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("project", "date", "description", "amount")
    list_filter = ("project", "date")
    search_fields = ("description", "project__name")
