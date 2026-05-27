from app.accounts.mixins import user_can_manage_system


def role_flags(request):
    can_manage_system = user_can_manage_system(request.user)
    return {
        "can_manage_system": can_manage_system,
        "show_categories_nav": can_manage_system,
        "show_locations_nav": can_manage_system,
        "show_suppliers_nav": can_manage_system,
        "show_clients_nav": can_manage_system,
        "show_tasks_nav": can_manage_system,
        "show_staff_nav": can_manage_system,
        "show_reports_nav": can_manage_system,
        "show_logs_nav": can_manage_system,
    }
