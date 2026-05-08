from django import forms
from .models import (
    Project,
    Employee,
    Attendance,
    PayrollPeriod,
    ProjectIncome,
    ProjectExpense,
)

DARK_INPUT = "form-control bg-dark text-light border-danger"
DARK_SELECT = "form-select bg-dark text-light border-danger"
DARK_CHECK = "form-check-input"


class BOProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(attrs={"class": DARK_INPUT}),
            "slug": forms.TextInput(attrs={"class": DARK_INPUT}),
            "contract_value": forms.NumberInput(attrs={"class": DARK_INPUT, "step": "0.01"}),
            "supervisors": forms.SelectMultiple(attrs={"class": DARK_SELECT}),
            "employees": forms.SelectMultiple(attrs={"class": DARK_SELECT}),
        }


class BOEmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = "__all__"
        widgets = {
            "full_name": forms.TextInput(attrs={"class": DARK_INPUT}),
            "position": forms.TextInput(attrs={"class": DARK_INPUT}),
            "hourly_rate": forms.NumberInput(attrs={"class": DARK_INPUT, "step": "0.01"}),
            "active": forms.CheckboxInput(attrs={"class": DARK_CHECK}),
        }


class BOAttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = "__all__"
        widgets = {
            "project": forms.Select(attrs={"class": DARK_SELECT}),
            "employee": forms.Select(attrs={"class": DARK_SELECT}),
            "date": forms.DateInput(attrs={"type": "date", "class": DARK_INPUT}),
            "check_in": forms.DateTimeInput(attrs={"type": "datetime-local", "class": DARK_INPUT}),
            "check_out": forms.DateTimeInput(attrs={"type": "datetime-local", "class": DARK_INPUT}),
        }


class BOPayrollPeriodForm(forms.ModelForm):
    class Meta:
        model = PayrollPeriod
        fields = "__all__"
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date", "class": DARK_INPUT}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": DARK_INPUT}),
            "project": forms.Select(attrs={"class": DARK_SELECT}),
            "status": forms.Select(attrs={"class": DARK_SELECT}),
            "created_by": forms.Select(attrs={"class": DARK_SELECT}),
        }


class BOIncomeForm(forms.ModelForm):
    class Meta:
        model = ProjectIncome
        fields = "__all__"
        widgets = {
            "project": forms.Select(attrs={"class": DARK_SELECT}),
            "date": forms.DateInput(attrs={"type": "date", "class": DARK_INPUT}),
            "amount": forms.NumberInput(attrs={"class": DARK_INPUT, "step": "0.01"}),
            "description": forms.TextInput(attrs={"class": DARK_INPUT}),
        }


class BOExpenseForm(forms.ModelForm):
    class Meta:
        model = ProjectExpense
        fields = "__all__"
        widgets = {
            "project": forms.Select(attrs={"class": DARK_SELECT}),
            "date": forms.DateInput(attrs={"type": "date", "class": DARK_INPUT}),
            "category": forms.Select(attrs={"class": DARK_SELECT}),
            "amount": forms.NumberInput(attrs={"class": DARK_INPUT, "step": "0.01"}),
            "description": forms.TextInput(attrs={"class": DARK_INPUT}),
        }