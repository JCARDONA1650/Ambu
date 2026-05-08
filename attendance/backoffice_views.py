from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import (
    Project,
    Employee,
    Attendance,
    PayrollPeriod,
    ProjectIncome,
    ProjectExpense,
)
from .backoffice_forms import (
    BOProjectForm,
    BOEmployeeForm,
    BOAttendanceForm,
    BOPayrollPeriodForm,
    BOIncomeForm,
    BOExpenseForm,
)


def is_admin_user(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)


def backoffice_list(
    request,
    model,
    template_name,
    context_name="items",
    search_fields=None,
    extra_context=None,
):
    qs = model.objects.all().order_by("-id")
    q = request.GET.get("q", "").strip()

    if q and search_fields:
        query = Q()
        for field in search_fields:
            query |= Q(**{f"{field}__icontains": q})
        qs = qs.filter(query)

    context = {
        context_name: qs,
        "q": q,
    }
    if extra_context:
        context.update(extra_context)
    return render(request, template_name, context)


def backoffice_form(request, form_class, template_name, title, instance=None, success_url=None):
    form = form_class(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        messages.success(request, f"{title} guardado correctamente.")
        return redirect(success_url)
    return render(request, template_name, {"form": form, "title": title, "obj": instance})


@login_required
@user_passes_test(is_admin_user)
def backoffice_dashboard(request):
    context = {
        "projects_count": Project.objects.count(),
        "employees_count": Employee.objects.count(),
        "attendance_count": Attendance.objects.count(),
        "payroll_count": PayrollPeriod.objects.count(),
        "income_count": ProjectIncome.objects.count(),
        "expense_count": ProjectExpense.objects.count(),
    }
    return render(request, "backoffice/dashboard.html", context)


# PROJECTS
@login_required
@user_passes_test(is_admin_user)
def bo_project_list(request):
    return backoffice_list(
        request,
        model=Project,
        template_name="backoffice/project_list.html",
        search_fields=["name", "slug"],
        extra_context={"title": "Proyectos"},
    )


@login_required
@user_passes_test(is_admin_user)
def bo_project_create(request):
    return backoffice_form(
        request,
        form_class=BOProjectForm,
        template_name="backoffice/form.html",
        title="Nuevo Proyecto",
        success_url="bo_project_list",
    )


@login_required
@user_passes_test(is_admin_user)
def bo_project_edit(request, pk):
    obj = get_object_or_404(Project, pk=pk)
    return backoffice_form(
        request,
        form_class=BOProjectForm,
        template_name="backoffice/form.html",
        title="Editar Proyecto",
        instance=obj,
        success_url="bo_project_list",
    )


@login_required
@user_passes_test(is_admin_user)
def bo_project_delete(request, pk):
    obj = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Proyecto eliminado correctamente.")
        return redirect("bo_project_list")
    return render(request, "backoffice/confirm_delete.html", {"obj": obj, "title": "Eliminar Proyecto"})


# EMPLOYEES
@login_required
@user_passes_test(is_admin_user)
def bo_employee_list(request):
    return backoffice_list(
        request,
        model=Employee,
        template_name="backoffice/employee_list.html",
        search_fields=["full_name", "position"],
        extra_context={"title": "Empleados"},
    )


@login_required
@user_passes_test(is_admin_user)
def bo_employee_create(request):
    return backoffice_form(
        request,
        form_class=BOEmployeeForm,
        template_name="backoffice/form.html",
        title="Nuevo Empleado",
        success_url="bo_employee_list",
    )


@login_required
@user_passes_test(is_admin_user)
def bo_employee_edit(request, pk):
    obj = get_object_or_404(Employee, pk=pk)
    return backoffice_form(
        request,
        form_class=BOEmployeeForm,
        template_name="backoffice/form.html",
        title="Editar Empleado",
        instance=obj,
        success_url="bo_employee_list",
    )


@login_required
@user_passes_test(is_admin_user)
def bo_employee_delete(request, pk):
    obj = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Empleado eliminado correctamente.")
        return redirect("bo_employee_list")
    return render(request, "backoffice/confirm_delete.html", {"obj": obj, "title": "Eliminar Empleado"})


# ATTENDANCE
@login_required
@user_passes_test(is_admin_user)
def bo_attendance_list(request):
    return backoffice_list(
        request,
        model=Attendance,
        template_name="backoffice/attendance_list.html",
        search_fields=["employee__full_name", "project__name"],
        extra_context={"title": "Asistencias"},
    )


@login_required
@user_passes_test(is_admin_user)
def bo_attendance_create(request):
    return backoffice_form(
        request,
        form_class=BOAttendanceForm,
        template_name="backoffice/form.html",
        title="Nueva Asistencia",
        success_url="bo_attendance_list",
    )


@login_required
@user_passes_test(is_admin_user)
def bo_attendance_edit(request, pk):
    obj = get_object_or_404(Attendance, pk=pk)
    return backoffice_form(
        request,
        form_class=BOAttendanceForm,
        template_name="backoffice/form.html",
        title="Editar Asistencia",
        instance=obj,
        success_url="bo_attendance_list",
    )


@login_required
@user_passes_test(is_admin_user)
def bo_attendance_delete(request, pk):
    obj = get_object_or_404(Attendance, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Asistencia eliminada correctamente.")
        return redirect("bo_attendance_list")
    return render(request, "backoffice/confirm_delete.html", {"obj": obj, "title": "Eliminar Asistencia"})


# PAYROLL
@login_required
@user_passes_test(is_admin_user)
def bo_payroll_list(request):
    return backoffice_list(
        request,
        model=PayrollPeriod,
        template_name="backoffice/payroll_list.html",
        search_fields=["project__name", "status"],
        extra_context={"title": "Nómina"},
    )


@login_required
@user_passes_test(is_admin_user)
def bo_payroll_create(request):
    return backoffice_form(
        request,
        form_class=BOPayrollPeriodForm,
        template_name="backoffice/form.html",
        title="Nuevo Período de Nómina",
        success_url="bo_payroll_list",
    )


@login_required
@user_passes_test(is_admin_user)
def bo_payroll_edit(request, pk):
    obj = get_object_or_404(PayrollPeriod, pk=pk)
    return backoffice_form(
        request,
        form_class=BOPayrollPeriodForm,
        template_name="backoffice/form.html",
        title="Editar Período de Nómina",
        instance=obj,
        success_url="bo_payroll_list",
    )


@login_required
@user_passes_test(is_admin_user)
def bo_payroll_delete(request, pk):
    obj = get_object_or_404(PayrollPeriod, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Período de nómina eliminado correctamente.")
        return redirect("bo_payroll_list")
    return render(request, "backoffice/confirm_delete.html", {"obj": obj, "title": "Eliminar Período de Nómina"})


# INCOMES
@login_required
@user_passes_test(is_admin_user)
def bo_income_list(request):
    return backoffice_list(
        request,
        model=ProjectIncome,
        template_name="backoffice/income_list.html",
        search_fields=["project__name", "description"],
        extra_context={"title": "Ingresos"},
    )


@login_required
@user_passes_test(is_admin_user)
def bo_income_create(request):
    return backoffice_form(
        request,
        form_class=BOIncomeForm,
        template_name="backoffice/form.html",
        title="Nuevo Ingreso",
        success_url="bo_income_list",
    )


@login_required
@user_passes_test(is_admin_user)
def bo_income_edit(request, pk):
    obj = get_object_or_404(ProjectIncome, pk=pk)
    return backoffice_form(
        request,
        form_class=BOIncomeForm,
        template_name="backoffice/form.html",
        title="Editar Ingreso",
        instance=obj,
        success_url="bo_income_list",
    )


@login_required
@user_passes_test(is_admin_user)
def bo_income_delete(request, pk):
    obj = get_object_or_404(ProjectIncome, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Ingreso eliminado correctamente.")
        return redirect("bo_income_list")
    return render(request, "backoffice/confirm_delete.html", {"obj": obj, "title": "Eliminar Ingreso"})


# EXPENSES
@login_required
@user_passes_test(is_admin_user)
def bo_expense_list(request):
    return backoffice_list(
        request,
        model=ProjectExpense,
        template_name="backoffice/expense_list.html",
        search_fields=["project__name", "description", "category"],
        extra_context={"title": "Gastos"},
    )


@login_required
@user_passes_test(is_admin_user)
def bo_expense_create(request):
    return backoffice_form(
        request,
        form_class=BOExpenseForm,
        template_name="backoffice/form.html",
        title="Nuevo Gasto",
        success_url="bo_expense_list",
    )


@login_required
@user_passes_test(is_admin_user)
def bo_expense_edit(request, pk):
    obj = get_object_or_404(ProjectExpense, pk=pk)
    return backoffice_form(
        request,
        form_class=BOExpenseForm,
        template_name="backoffice/form.html",
        title="Editar Gasto",
        instance=obj,
        success_url="bo_expense_list",
    )


@login_required
@user_passes_test(is_admin_user)
def bo_expense_delete(request, pk):
    obj = get_object_or_404(ProjectExpense, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Gasto eliminado correctamente.")
        return redirect("bo_expense_list")
    return render(request, "backoffice/confirm_delete.html", {"obj": obj, "title": "Eliminar Gasto"})