import logging, sys, structlog

def init_logging(app):
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(message)s",
    )
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    app.logger.setLevel(logging.INFO)
