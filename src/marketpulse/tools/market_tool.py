import logging
logging.getLogger('opentelemetry.trace').setLevel(logging.ERROR)

from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from langchain_community.utilities import GoogleSerperAPIWrapper
import os
import requests
from datetime import datetime, timedelta
import json

class NewsSearchInput(BaseModel):
    """Input schema for NewsSearchTool."""
    query: str = Field(
        ...,
        description="Search query to find financial news."
    )

class FinancialNewsSearchTool(BaseTool):
    name: str = "financial_news_search"
    description: str = (
        "Use this tool to search for financial and economic news. "
        "It can find articles about companies, sectors, economic indicators, "
        "and market trends from financial news sources."
    )
    args_schema: Type[BaseModel] = NewsSearchInput
    search_wrapper: GoogleSerperAPIWrapper = None

    def __init__(self):
        super().__init__()
        self.search_wrapper = GoogleSerperAPIWrapper(serper_api_key=os.getenv('SERPER_API_KEY'))

    def _run(self, query: str) -> str:
        """Run the tool with caching and usage tracking"""
        cache_dir = ".cache/news"
        os.makedirs(cache_dir, exist_ok=True)
        
        # Create a cache key based on the query
        cache_key = "".join(x for x in query if x.isalnum() or x.isspace()).lower().replace(" ", "_")
        cache_file = f"{cache_dir}/{cache_key}.json"
        
        # Check if we have a cached result for this query from today
        if os.path.exists(cache_file):
            file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
            if file_time.date() == datetime.now().date():
                with open(cache_file, 'r') as f:
                    return f.read()
        
        # If no cache or cache is old, make the actual API call
        try:
            results = self.search_wrapper.run(f"financial news {query}")
            
            # Create logs directory if it doesn't exist
            os.makedirs(".logs", exist_ok=True)
            
            # Log usage
            with open(".logs/serper_usage.log", "a") as log:
                log.write(f"{datetime.now().isoformat()},query,{query}\n")
            
            # Cache the results
            with open(cache_file, 'w') as f:
                f.write(results)
                
            return results
        except Exception as e:
            return f"Error performing search: {str(e)}"


class StockQuoteInput(BaseModel):
    """Input schema for StockQuoteSearchTool."""
    symbol: str = Field(
        ...,
        description="Stock ticker symbol to get quote data for."
    )

class StockQuoteTool(BaseTool):
    name: str = "stock_quote"
    description: str = (
        "Use this tool to get current stock price data and basic information. "
        "Provide a ticker symbol to get current price, change, volume, market cap, "
        "and other basic data."
    )
    args_schema: Type[BaseModel] = StockQuoteInput

    def _run(self, symbol: str) -> str:
        """Run the tool to get stock quote data"""
        cache_dir = ".cache/quotes"
        os.makedirs(cache_dir, exist_ok=True)
        
        # Create a cache file for this symbol
        cache_file = f"{cache_dir}/{symbol.upper()}.json"
        
        # Check if we have a recent cached result (less than 1 hour old)
        if os.path.exists(cache_file):
            file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
            if datetime.now() - file_time < timedelta(hours=1):
                with open(cache_file, 'r') as f:
                    return f.read()
        
        # If no cache or cache is old, make the actual API call
        try:
            # Using Alpha Vantage API as an example
            api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
            
            response = requests.get(url)
            data = response.json()
            
            # Create logs directory if it doesn't exist
            os.makedirs(".logs", exist_ok=True)
            
            # Log usage
            with open(".logs/alphavantage_usage.log", "a") as log:
                log.write(f"{datetime.now().isoformat()},quote,{symbol}\n")
            
            # Format the response
            if "Global Quote" in data and data["Global Quote"]:
                quote = data["Global Quote"]
                result = {
                    "symbol": quote.get("01. symbol", ""),
                    "price": quote.get("05. price", ""),
                    "change": quote.get("09. change", ""),
                    "change_percent": quote.get("10. change percent", ""),
                    "volume": quote.get("06. volume", ""),
                    "latest_trading_day": quote.get("07. latest trading day", "")
                }
                formatted_result = json.dumps(result, indent=2)
                
                # Cache the result
                with open(cache_file, 'w') as f:
                    f.write(formatted_result)
                
                return formatted_result
            else:
                return f"Error: Could not retrieve quote data for {symbol}."
                
        except Exception as e:
            return f"Error retrieving stock quote: {str(e)}"


class InfluencerMonitorInput(BaseModel):
    """Input schema for InfluencerMonitorTool."""
    person: str = Field(
        ...,
        description="Name of the key market influencer to monitor (e.g., 'Elon Musk', 'Jerome Powell')."
    )

class InfluencerMonitorTool(BaseTool):
    name: str = "influencer_monitor"
    description: str = (
        "Use this tool to monitor recent statements or actions from key market influencers "
        "like Elon Musk, Jerome Powell, business leaders, or government officials."
    )
    args_schema: Type[BaseModel] = InfluencerMonitorInput
    search_wrapper: GoogleSerperAPIWrapper = None

    def __init__(self):
        super().__init__()
        self.search_wrapper = GoogleSerperAPIWrapper(serper_api_key=os.getenv('SERPER_API_KEY'))

    def _run(self, person: str) -> str:
        """Run the tool with caching mechanism"""
        cache_dir = ".cache/influencers"
        os.makedirs(cache_dir, exist_ok=True)
        
        # Create a safe filename
        safe_name = "".join(x for x in person if x.isalnum() or x.isspace()).lower().replace(" ", "_")
        cache_file = f"{cache_dir}/{safe_name}.json"
        
        # Check if we have a recent cached result (less than 4 hours old)
        if os.path.exists(cache_file):
            file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
            if datetime.now() - file_time < timedelta(hours=4):
                with open(cache_file, 'r') as f:
                    return f.read()
        
        # If no cache or cache is old, make the actual API call
        try:
            # Craft a query focused on recent statements/actions with market impact
            query = f"{person} recent statement market finance economy (site:cnbc.com OR site:bloomberg.com OR site:reuters.com OR site:ft.com OR site:wsj.com)"
            results = self.search_wrapper.run(query)
            
            # Create logs directory if it doesn't exist
            os.makedirs(".logs", exist_ok=True)
            
            # Log usage
            with open(".logs/serper_usage.log", "a") as log:
                log.write(f"{datetime.now().isoformat()},influencer,{person}\n")
            
            # Cache the results
            with open(cache_file, 'w') as f:
                f.write(results)
                
            return results
        except Exception as e:
            return f"Error monitoring influencer: {str(e)}"