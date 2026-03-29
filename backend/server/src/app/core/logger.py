import logging

import structlog

from .config import settings

# Shared processors
SHARED_PROCESSORS: list[structlog.types.Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.StackInfoRenderer(),
]

structlog.configure(
    processors=SHARED_PROCESSORS + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

_formatter = structlog.stdlib.ProcessorFormatter(
    foreign_pre_chain=SHARED_PROCESSORS,
    processors=[
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        structlog.dev.ConsoleRenderer()
        if settings.ENVIRONMENT.value == "local"
        else structlog.processors.JSONRenderer(),
    ],
)

_handler = logging.StreamHandler()
_handler.setFormatter(_formatter)

root_logger = logging.getLogger()
root_logger.handlers.clear()
root_logger.addHandler(_handler)
root_logger.setLevel(settings.LOG_LEVEL)

for _name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
    _log = logging.getLogger(_name)
    _log.handlers.clear()
    _log.propagate = True
