from abc import ABC, abstractmethod
from typing import Any


class EventBus(ABC):
    """Port for publishing domain events."""
    
    @abstractmethod
    def publish(self, event: Any) -> None:
        pass