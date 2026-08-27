from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class HomeCache(ABC):
    """
    Port for home cache operations.
    """
    @abstractmethod
    def get_home_page_data(self) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def set_home_page_data(self, data: Dict[str, Any]) -> None:
        pass