from typing import Any
from home.application.ports.readers import HomePageReader

class GetAboutPageQuery:
    """
    Use case for retrieving active About Us content.
    """
    def __init__(self, reader: HomePageReader) -> None:
        self.reader = reader

    def execute(self) -> Any:
        return self.reader.get_about_page_content()