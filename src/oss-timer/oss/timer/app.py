from oss.core.log import Log
from oss.core.models.base.app import BaseApp
from oss.core.models.timers import Timer
from oss.core.models.base.timer import BaseTimer

# Activate module wide logging
logger = Log.get_logger_function()(__name__)


class TimerApp(BaseApp):
    _timer: BaseTimer

    def __init__(self, timer: Timer) -> None:
        # If there are timers as a parameter, add them to the timer list.
        if timer:
            # Initialize the passed in timer and make it the timer of this timer app
            self._timer = timer.value()
            logger.info(self._identifier)
        else:
            # We have a major problem a timer app without a timer
            logger.critical("Cannot start app. No timer or invalid timer specified")
            self.terminate()

    def __del__(self):
        self.terminate()

    def run(self) -> None:
        while True:
            # don't have much to do right now :)
            pass

    def terminate(self) -> None:
        # Terminate old connections to the message broker
        pass


app: TimerApp = TimerApp(timer=Timer.STAGE)
app.run()
