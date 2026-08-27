from typing import Dict, Any
from home.application.ports.readers import HomePageReader

class GetHomePageDataQuery:
    """
    Use case for retrieving aggregated home page data.
    """
    def __init__(self, reader: HomePageReader) -> None:
        self.reader = reader

    def execute(self) -> Dict[str, Any]:
        return self.reader.get_aggregated_data()