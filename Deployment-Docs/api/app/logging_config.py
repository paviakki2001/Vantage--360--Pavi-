import logging
from api.app.config import settings


logger = logging.getLogger(__name__)
audit_logger = logging.getLogger("vantage360.audit")

def setup_logging():
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    return logging.getLogger(settings.service_name)
