# attendance/decorators.py
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

def groups_required(*group_names):
    """
    Restringe la vista a usuarios logueados que pertenezcan a alguno de los grupos dados.
    Uso:
    @groups_required('Manager', 'Supervisor')
    """
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if request.user.groups.filter(name__in=group_names).exists():
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("No tienes permisos para acceder a esta vista.")
        return _wrapped
    return decorator
