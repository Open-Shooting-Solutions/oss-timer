from abc import ABC, abstractmethod
from uuid import UUID, uuid4
from oss.core.message import BrokerConnection


class BaseTimer(ABC):
    # Each timer needs an uuid so we can keep track of which timer triggered an action.
    # This is mostly for debugging.
    _identifier: UUID = uuid4()

    # Each remote needs an connection to the message broker to send commands
    _broker_connection: BrokerConnection

    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def __del__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def _handle_broker_message(self, ch, method, properties, body) -> None:
        raise NotImplementedError
