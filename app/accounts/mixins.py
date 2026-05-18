from django.contrib.auth.mixins import UserPassesTestMixin

from app.accounts.constants import ROLE_MANAGER


def user_has_role(user, *roles: str) -> bool:
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=roles).exists()


class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles: tuple[str, ...] = tuple()

    def test_func(self):
        return user_has_role(self.request.user, *self.allowed_roles)


class ManagerRequiredMixin(RoleRequiredMixin):
    allowed_roles = (ROLE_MANAGER,)
