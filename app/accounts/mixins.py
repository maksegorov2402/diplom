from django.contrib.auth.mixins import UserPassesTestMixin

from app.accounts.constants import ROLE_ADMIN, ROLE_MANAGER

MANAGEMENT_ROLES = (ROLE_ADMIN, ROLE_MANAGER)


def user_has_role(user, *roles: str) -> bool:
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=roles).exists()


def user_can_manage_system(user) -> bool:
    return user_has_role(user, *MANAGEMENT_ROLES)


class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles: tuple[str, ...] = tuple()

    def test_func(self):
        return user_has_role(self.request.user, *self.allowed_roles)


class ModelFormTitleMixin:
    form_title: str | None = None

    def get_form_title(self) -> str:
        if self.form_title:
            return self.form_title
        return self.model._meta.verbose_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = self.get_form_title()
        return context


class ManagerRequiredMixin(RoleRequiredMixin):
    allowed_roles = MANAGEMENT_ROLES
