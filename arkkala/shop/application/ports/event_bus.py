from abc import ABC, abstractmethod
from typing import Any

class EventBusPort(ABC):
    """Interface for publishing domain events."""
    
    @abstractmethod
    def publish(self, event: Any) -> None:
        """Publishes the given event payload to the bus."""
        pass