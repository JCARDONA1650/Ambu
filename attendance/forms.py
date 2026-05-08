# attendance/forms.py
from django import forms
from .models import (
    Employee, PayrollPeriod, PayrollLine, Project,
    ProjectIncome, ProjectExpense
)
# ──────────────────────────────────────────────
# Opciones
# ──────────────────────────────────────────────
# ──────────────────────────────────────────────
# Opciones
# ──────────────────────────────────────────────
from django import forms
from .models import Employee

ACTIONS = (
    ("IN", "Check-In (Ingreso)"),
    ("OUT", "Check-Out (Salida)"),
)

class ScanForm(forms.Form):
    employee = forms.ModelChoiceField(
        label="Empleado",
        queryset=Employee.objects.none(),
        widget=forms.Select(attrs={
            "class": "form-select bg-dark text-light border-danger"
        })
    )
    action = forms.ChoiceField(
        label="Acción",
        choices=ACTIONS,
        widget=forms.Select(attrs={
            "class": "form-select bg-dark text-light border-danger"
        })
    )
    evidence_photo = forms.ImageField(
        label="Tomar foto (obligatoria)",
        required=True,
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control bg-dark text-light border-danger",
            "accept": "image/*",
            "capture": "environment",
        })
    )

    # 🔒 Campos para idempotencia/confirmación servidor
    client_uuid = forms.CharField(required=False, max_length=64, widget=forms.HiddenInput())
    device_ts   = forms.CharField(required=False, max_length=40, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)
        if project and project.employees.exists():
            self.fields["employee"].queryset = (
                project.employees.filter(active=True).order_by("full_name")
            )
        else:
            self.fields["employee"].queryset = (
                Employee.objects.filter(active=True).order_by("full_name")
            )

    # Validación mínima por seguridad
    def clean_evidence_photo(self):
        photo = self.cleaned_data.get("evidence_photo")
        if not photo:
            raise forms.ValidationError("Debes tomar o adjuntar una foto.")
        allowed = {"image/jpeg", "image/png", "image/webp"}
        if hasattr(photo, "content_type") and photo.content_type not in allowed:
            raise forms.ValidationError("Formato no permitido. Usa JPG, PNG o WEBP.")
        if photo.size > 6 * 1024 * 1024:
            raise forms.ValidationError("La foto no puede superar 6 MB.")
        return photo

# Empleados
# ──────────────────────────────────────────────
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ["full_name", "position", "hourly_rate", "active"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control bg-dark text-light border-danger"}),
            "position": forms.TextInput(attrs={"class": "form-control bg-dark text-light border-danger"}),
            "hourly_rate": forms.NumberInput(attrs={"class": "form-control bg-dark text-light border-danger", "step": "0.01"}),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

# ──────────────────────────────────────────────
# Nómina
# ──────────────────────────────────────────────
class PayrollPeriodForm(forms.ModelForm):
    class Meta:
        model = PayrollPeriod
        fields = ["start_date", "end_date", "project"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control bg-dark text-light border-danger"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control bg-dark text-light border-danger"}),
            "project": forms.Select(attrs={"class": "form-select bg-dark text-light border-danger"}),
        }

class PayrollLineAdjustmentForm(forms.ModelForm):
    class Meta:
        model = PayrollLine
        fields = ["adjustment", "notes"]
        widgets = {
            "adjustment": forms.NumberInput(attrs={"class": "form-control bg-dark text-light border-danger", "step": "0.01"}),
            "notes": forms.TextInput(attrs={"class": "form-control bg-dark text-light border-danger"}),
        }

# ──────────────────────────────────────────────
# Exportar nómina
# ──────────────────────────────────────────────
class PayrollExportForm(forms.Form):
    SCOPE_CHOICES = (
        ("quincena", "Quincena"),
        ("mes", "Mes"),
        ("anio", "Año"),
    )
    scope = forms.ChoiceField(label="Ámbito", choices=SCOPE_CHOICES, widget=forms.Select(attrs={"class": "form-select bg-dark text-light border-danger"}))
    project = forms.ModelChoiceField(queryset=Project.objects.all(), required=False, widget=forms.Select(attrs={"class": "form-select bg-dark text-light border-danger"}))
    month = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "month", "class": "form-control bg-dark text-light border-danger"}))
    year = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={"class": "form-control bg-dark text-light border-danger"}))
    half = forms.ChoiceField(label="Quincena", required=False, choices=(("1","Primera"),("2","Segunda")), widget=forms.Select(attrs={"class": "form-select bg-dark text-light border-danger"}))

# ──────────────────────────────────────────────
# Finanzas de Proyecto
# ──────────────────────────────────────────────
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "contract_value", "supervisors", "employees"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control bg-dark text-light border-danger"}),
            "contract_value": forms.NumberInput(attrs={"class": "form-control bg-dark text-light border-danger", "step": "0.01"}),
            "supervisors": forms.SelectMultiple(attrs={"class": "form-select bg-dark text-light border-danger"}),
            "employees": forms.SelectMultiple(attrs={"class": "form-select bg-dark text-light border-danger"}),
        }

class IncomeForm(forms.ModelForm):
    class Meta:
        model = ProjectIncome
        fields = ["project", "date", "amount", "description"]
        widgets = {
            "project": forms.Select(attrs={"class": "form-select bg-dark text-light border-danger"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control bg-dark text-light border-danger"}),
            "amount": forms.NumberInput(attrs={"class": "form-control bg-dark text-light border-danger", "step": "0.01"}),
            "description": forms.TextInput(attrs={"class": "form-control bg-dark text-light border-danger"}),
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = ProjectExpense
        fields = ["project", "date", "category", "amount", "description"]
        widgets = {
            "project": forms.Select(attrs={"class": "form-select bg-dark text-light border-danger"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control bg-dark text-light border-danger"}),
            "category": forms.Select(attrs={"class": "form-select bg-dark text-light border-danger"}),
            "amount": forms.NumberInput(attrs={"class": "form-control bg-dark text-light border-danger", "step": "0.01"}),
            "description": forms.TextInput(attrs={"class": "form-control bg-dark text-light border-danger"}),
        }

