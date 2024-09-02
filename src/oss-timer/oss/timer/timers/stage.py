from typing import Callable
from oss.core.log import Log
from oss.core.message import BrokerConnection, BrokerExchangeType, BrokerMessage
from oss.core.models.base.timer import BaseTimer
from oss.core.models.base.timer import TimerControl

# Activate module wide logging
logger = Log.get_logger_function()(__name__)


class StageTimer(BaseTimer):
    _timer_controls: dict[TimerControl, Callable] = {}

    def __init__(self) -> None:
        self._map_timer_controls()
        self._broker_connection = BrokerConnection(host="localhost", port=5672)
        self._broker_connection.setup_channel(name="remote", exchange_type=BrokerExchangeType.TOPIC)
        self._broker_connection.channel.queue_declare("remote", exclusive=True)
        self._broker_connection.channel.queue_bind(exchange="remote", queue="remote", routing_key="remote.*.action")
        self._broker_connection.channel.basic_consume(
            queue="remote", on_message_callback=self._handle_broker_message, auto_ack=True
        )
        self._broker_connection.channel.start_consuming()

    def __del__(self) -> None:
        pass

    def _map_timer_controls(self):
        self._timer_controls.update({TimerControl.TOGGLE_PHASE: self._toggle_phase})
        self._timer_controls.update({TimerControl.RESET_PHASE: self._reset_phase})

    def _handle_broker_message(self, ch, method, properties, body) -> None:
        broker_message: BrokerMessage = BrokerMessage.from_json(body)

        try:
            action_name: str = broker_message.body["action"]  # Access the "action" field
            timer_control: TimerControl = TimerControl(action_name)

            timer_function: Callable = self._timer_controls[timer_control]
            timer_function()
        except:
            logger.error("Failed to call functionaaa")

    def _toggle_phase(self):
        print("toggle phase function")

    def _reset_phase(self):
        print("reset phase function")
