from typing import Protocol, Any

class EventBusPort(Protocol):
    def publish(self, event: Any) -> None: ...