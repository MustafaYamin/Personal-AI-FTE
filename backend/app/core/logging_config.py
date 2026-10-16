import logging
import sys


def configure_logging(debug: bool) -> None:
    """One structured logging setup shared by every feature — features should
    just call `logging.getLogger(__name__)`, never configure handlers themselves."""
    level = logging.DEBUG if debug else logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s [%(request_id)s] %(message)s",
            defaults={"request_id": "-"},
        )
    )
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]

    # Quiet noisy third-party loggers at INFO+ unless we're debugging.
    if not debug:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
