from oss.core.log import Log
from oss.core.models.base.app import BaseApp
from oss.timer.models.timer import BaseTimer

# Activate module wide logging
logger = Log.get_logger_function()(__name__)


class TimerApp(BaseApp):
    _timers: list[BaseTimer] = []

    def __init__(self, timers: Optional[list[Timer]]) -> None:
        # If there are buzzers as a parameter, add them to the buzzer list.
        if timers:
            for timer in timers:
                self._timers.append(timer.value)
        else:
            # We have a major problem a timer app without a timer
            pass

    def run(self) -> None:
        # Create a connection to the message broker
        pass

    def terminate(self) -> None:
        # Terminate old connections to the message broker
        pass
