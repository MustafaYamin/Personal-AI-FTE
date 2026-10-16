"""Just the shared Base — nothing else. Feature models import `Base` from
`app.models.base` directly; if this __init__ also imported those feature
models (for Alembic's benefit), it would create a circular import, since
Python always runs a package's __init__ before any of its submodules, and
`app.features.auth.models` imports `app.models.base` (a submodule of this
very package) before it has finished defining its own classes.

Alembic needs every feature's models imported before it reads
Base.metadata — that happens in alembic/env.py instead, not here."""

from app.models.base import Base  # noqa: F401
