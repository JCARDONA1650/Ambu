from django.urls import path
from . import views
from . import backoffice_views as bo

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("<slug:project_slug>/scan/", views.scan_view, name="scan"),
    path("<slug:project_slug>/qr/", views.qr_scan_view, name="qr_scan"),
    path("report/", views.report_view, name="report"),

    path("<slug:project_slug>/kiosk/", views.scan_kiosk_view, name="scan_kiosk"),
 


    # Empleados
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/new/", views.employee_form, name="employee_new"),
    path("employees/<int:pk>/edit/", views.employee_form, name="employee_edit"),

    # Nómina
    path("payroll/", views.payroll_list, name="payroll_list"),
    path("payroll/new/", views.payroll_new, name="payroll_new"),
    path("payroll/<int:pk>/", views.payroll_detail, name="payroll_detail"),
    path("payroll/<int:pk>/recalc/", views.payroll_recalc, name="payroll_recalc"),
    path("payroll/<int:pk>/close/", views.payroll_close, name="payroll_close"),

    # 
    path("payroll/export/", views.payroll_export_xlsx, name="payroll_export_xlsx"),
    path("payroll/export-pdf/", views.payroll_export_pdf, name="payroll_export_pdf"),

    # Finanzas de proyectos (solo admin)
    path("projects/new/", views.project_new, name="project_new"),
    path("incomes/new/", views.income_new, name="income_new"),
    path("expenses/new/", views.expense_new, name="expense_new"),
    path("projects/<slug:project_slug>/finance/", views.project_finance_dashboard,
         name="project_finance_dashboard"),

    path("backoffice/", bo.backoffice_dashboard, name="backoffice"),

    path("backoffice/projects/", bo.bo_project_list, name="bo_project_list"),
    path("backoffice/projects/new/", bo.bo_project_create, name="bo_project_create"),
    path("backoffice/projects/<int:pk>/edit/", bo.bo_project_edit, name="bo_project_edit"),
    path("backoffice/projects/<int:pk>/delete/", bo.bo_project_delete, name="bo_project_delete"),

    path("backoffice/employees/", bo.bo_employee_list, name="bo_employee_list"),
    path("backoffice/employees/new/", bo.bo_employee_create, name="bo_employee_create"),
    path("backoffice/employees/<int:pk>/edit/", bo.bo_employee_edit, name="bo_employee_edit"),
    path("backoffice/employees/<int:pk>/delete/", bo.bo_employee_delete, name="bo_employee_delete"),

    path("backoffice/attendance/", bo.bo_attendance_list, name="bo_attendance_list"),
    path("backoffice/attendance/new/", bo.bo_attendance_create, name="bo_attendance_create"),
    path("backoffice/attendance/<int:pk>/edit/", bo.bo_attendance_edit, name="bo_attendance_edit"),
    path("backoffice/attendance/<int:pk>/delete/", bo.bo_attendance_delete, name="bo_attendance_delete"),

    path("backoffice/payroll/", bo.bo_payroll_list, name="bo_payroll_list"),
    path("backoffice/payroll/new/", bo.bo_payroll_create, name="bo_payroll_create"),
    path("backoffice/payroll/<int:pk>/edit/", bo.bo_payroll_edit, name="bo_payroll_edit"),
    path("backoffice/payroll/<int:pk>/delete/", bo.bo_payroll_delete, name="bo_payroll_delete"),

    path("backoffice/incomes/", bo.bo_income_list, name="bo_income_list"),
    path("backoffice/incomes/new/", bo.bo_income_create, name="bo_income_create"),
    path("backoffice/incomes/<int:pk>/edit/", bo.bo_income_edit, name="bo_bo_income_edit"),
    path("backoffice/incomes/<int:pk>/delete/", bo.bo_income_delete, name="bo_income_delete"),

    path("backoffice/expenses/", bo.bo_expense_list, name="bo_expense_list"),
    path("backoffice/expenses/new/", bo.bo_expense_create, name="bo_expense_create"),
    path("backoffice/expenses/<int:pk>/edit/", bo.bo_expense_edit, name="bo_expense_edit"),
    path("backoffice/expenses/<int:pk>/delete/", bo.bo_expense_delete, name="bo_expense_delete"),
]







