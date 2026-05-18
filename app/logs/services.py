from django.db import transaction

from app.logs.models import OperationLog


@transaction.atomic
def log_operation(*, user, operation_type: str, entity, description: str) -> OperationLog:
    entity_id = getattr(entity, "pk", None) or 0
    entity_type = entity.__class__.__name__
    return OperationLog.objects.create(
        user=user,
        operation_type=operation_type,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
    )
