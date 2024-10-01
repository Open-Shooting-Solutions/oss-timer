import threading
from typing import Callable

from oss.core.models.discipline.disciplines import StageBasedDiscipline, Disciplines
from oss.core.log import Log
from oss.core.message import BrokerConnection, BrokerExchangeType, BrokerMessage
from oss.core.models.base.timer import BaseTimer
from oss.core.models.base.timer import TimerControl


# Activate module wide logging
logger = Log.get_logger_function()(__name__)


class StageTimer(BaseTimer):
    _timer_controls: dict[TimerControl, Callable] = {}
    _discipline_configuration: [StageBasedDiscipline | Disciplines]
    _broker_connection: BrokerConnection

    def __init__(self) -> None:
        # self._discipline_configuration = Discipline.get(DisciplineFilename.SERVICE_PISTOOL)
        self._map_timer_controls()
        self._broker_connection = self._setup_broker_connection()

    def __del__(self) -> None:
        pass

    def _setup_broker_connection(self) -> BrokerConnection:
        broker_connection = BrokerConnection(host="localhost", port=5672)
        broker_connection.setup_channel(name="remote", exchange_type=BrokerExchangeType.TOPIC)
        broker_connection.channel.queue_declare(queue="remote", exclusive=True)
        broker_connection.channel.queue_bind(exchange="remote", queue="remote", routing_key="remote.*.action")
        broker_connection.channel.basic_consume(
            queue="remote",
            on_message_callback=self._handle_broker_message,
            auto_ack=True,
        )
        broker_connection.channel.start_consuming()
        return broker_connection

    def _map_timer_controls(self):
        self._timer_controls.update(
            {
                TimerControl.TOGGLE_PHASE: self._toggle_phase,
                TimerControl.RESET_PHASE: self._reset_phase,
            }
        )

    def _handle_broker_message(self, ch, method, properties, body) -> None:
        broker_message: BrokerMessage = BrokerMessage.from_json(body)
        try:
            action_name: str = broker_message.body["action"]  # Access the "action" field
            timer_control = TimerControl(action_name)
            timer_function = self._timer_controls[timer_control]
            timer_function()
        except KeyError:
            logger.error("Invalid action in broker message")

    def _toggle_phase(self) -> None:
        print(Discipline)

    def _reset_phase(self) -> None:
        print("reset phase function")
