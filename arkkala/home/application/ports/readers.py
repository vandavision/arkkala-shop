from abc import ABC, abstractmethod
from typing import Dict, Any

class HomePageReader(ABC):
    """
    Port for projecting aggregated home page data.
    """
    @abstractmethod
    def get_aggregated_data(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_site_settings(self) -> Any:
        pass

    @abstractmethod
    def get_active_faqs(self) -> Any:
        pass

    @abstractmethod
    def get_about_page_content(self) -> Any:
        pass