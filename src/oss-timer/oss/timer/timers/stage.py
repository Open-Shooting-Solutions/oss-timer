from oss.core.log import Log
from oss.core.message import BrokerConnection, BrokerExchangeType
from oss.timer.models.timer import BaseTimer

# Activate module wide logging
logger = Log.get_logger_function()(__name__)


class StageTimer(BaseTimer):
    def __init__(self) -> None:
        self._broker_connection = BrokerConnection(host="localhost", port=5672)
        self._broker_connection.setup_channel(name="remote", exchange_type=BrokerExchangeType.TOPIC)
        self._broker_connection.channel.queue_declare("remote", exclusive=True)
        self._broker_connection.channel.queue_bind(exchange="remote", queue="remote", routing_key="remote.*.action")
        self._broker_connection.channel.basic_consume(
            queue="remote", on_message_callback=self._handle_broker_message, auto_ack=True
        )

        self._broker_connection.channel.start_consuming()

        # Create a mapping from timer controls to timer....!!!

        # Could also create listener functions per topic.
        # def _handle_timer_toggle
        # def _handle_timer_....

    def __del__(self) -> None:
        pass

    def _handle_broker_message(self, ch, method, properties, body) -> None:
        pass
