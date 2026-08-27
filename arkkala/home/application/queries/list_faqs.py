from typing import Any
from home.application.ports.readers import HomePageReader

class ListFAQsQuery:
    """
    Use case for listing active FAQs.
    """
    def __init__(self, reader: HomePageReader) -> None:
        self.reader = reader

    def execute(self) -> Any:
        return self.reader.get_active_faqs()