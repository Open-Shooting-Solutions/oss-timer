# For LG, KKP, ETC etc.
from oss.core.log import Log
from oss.core.models.base.timer import BaseTimer

# Activate module wide logging
logger = Log.get_logger_function()(__name__)


class CompetitionTimer(BaseTimer):
    def __init__(self) -> None:
        pass

    def __del__(self) -> None:
        pass

    def _handle_broker_message(self, ch, method, properties, body) -> None:
        pass
