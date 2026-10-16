from enum import StrEnum


class OrgRole(StrEnum):
    """RBAC roles, ordered weakest to strongest. Every org-scoped endpoint
    declares its minimum role via `require_role(...)` in core/dependencies.py."""

    VIEWER = "viewer"
    MEMBER = "member"
    ADMIN = "admin"
    OWNER = "owner"


_ROLE_RANK = {role: i for i, role in enumerate(OrgRole)}


def role_at_least(role: OrgRole, minimum: OrgRole) -> bool:
    return _ROLE_RANK[role] >= _ROLE_RANK[minimum]


class ActionType(StrEnum):
    """Ported from the legacy audit_logger.py ActionType enum — kept stable
    since it's the audit_events.action_type value every feature writes."""

    EMAIL_SEND = "email_send"
    EMAIL_DRAFT = "email_draft"
    WHATSAPP_SEND = "whatsapp_send"
    LINKEDIN_POST = "linkedin_post"
    LINKEDIN_ENGAGE = "linkedin_engage"
    PAYMENT_INITIATE = "payment_initiate"
    PAYMENT_APPROVE = "payment_approve"
    FILE_CREATE = "file_create"
    FILE_MOVE = "file_move"
    FILE_DELETE = "file_delete"
    TASK_PROCESS = "task_process"
    APPROVAL_REQUEST = "approval_request"
    APPROVAL_GRANT = "approval_grant"
    APPROVAL_REJECT = "approval_reject"
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"

    # Phase-1-specific additions not present in the legacy enum:
    USER_SIGNUP = "user_signup"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    ORG_CREATE = "org_create"
    ORG_MEMBER_INVITE = "org_member_invite"
    ORG_MEMBER_JOIN = "org_member_join"
    ORG_MEMBER_ROLE_CHANGE = "org_member_role_change"
    ORG_MEMBER_REMOVE = "org_member_remove"

    ERROR = "error"
    GENERIC = "generic"


class ApprovalStatus(StrEnum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ActionResult(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"
