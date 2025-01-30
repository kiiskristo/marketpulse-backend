from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from langchain_community.utilities import BingSearchAPIWrapper
import os


class SearchToolInput(BaseModel):
    """Input schema for MarketSearchTool."""
    query: str = Field(
        ...,
        description="Search query to find market information, rankings, or company details."
    )


class MarketSearchTool(BaseTool):
    name: str = "market_search"
    description: str = (
        "Use this tool to search for market information, company rankings, "
        "and competitive analysis data. It performs web searches focused on "
        "business and market intelligence."
    )
    args_schema: Type[BaseModel] = SearchToolInput

    def __init__(self):
        super().__init__()
        self.bing = BingSearchAPIWrapper(
            bing_subscription_key=os.getenv('BING_SUBSCRIPTION_KEY'),
            bing_search_url="https://api.bing.microsoft.com/v7.0/search"
        )

    def _run(self, query: str) -> str:
        try:
            results = self.bing.run(query)
            return results
        except Exception as e:
            return f"Error performing search: {str(e)}"