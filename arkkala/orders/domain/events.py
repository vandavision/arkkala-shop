from dataclasses import dataclass
from typing import Optional


@dataclass
class OrderCreatedEvent:
    """Event published when a new order is successfully created."""
    order_uuid: str
    user_email: Optional[str]