import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    actor_id: uuid.UUID | None
    actor_type: str
    action_type: str
    target: str
    parameters: dict
    approval_status: str
    approved_by_id: uuid.UUID | None
    result: str
    error_message: str | None
    event_metadata: dict
