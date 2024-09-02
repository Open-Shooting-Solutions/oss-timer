from oss.core.log import Log
from oss.core.models.base.app import BaseApp
from oss.core.models.timers import Timer
from oss.core.models.base.timer import BaseTimer

# Activate module wide logging
logger = Log.get_logger_function()(__name__)


class TimerApp(BaseApp):
    _timers: list[BaseTimer] = []

    def __init__(self, timers: list[Timer]) -> None:
        # If there are buzzers as a parameter, add them to the buzzer list.
        if timers:
            for timer in timers:
                self._timers.append(timer.value())
        else:
            # We have a major problem a timer app without a timer
            pass

    def run(self) -> None:
        while True:
            # don't have much to do right now :)
            pass

    def terminate(self) -> None:
        # Terminate old connections to the message broker
        pass


app: TimerApp = TimerApp(timers=[Timer.STAGE])
app.run()
