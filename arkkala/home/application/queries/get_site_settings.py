from typing import Any
from home.application.ports.readers import HomePageReader

class GetSiteSettingsQuery:
    """
    Use case for retrieving global site settings.
    """
    def __init__(self, reader: HomePageReader) -> None:
        self.reader = reader

    def execute(self) -> Any:
        return self.reader.get_site_settings()