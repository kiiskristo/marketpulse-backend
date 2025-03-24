#!/usr/bin/env python
import sys
import json
import yaml
import warnings
import asyncio
from datetime import datetime
import argparse
from typing import Dict, Any
import os

from .flows.market_analysis_flow import MarketSentimentFlow

warnings.filterwarnings("ignore", category=SyntaxWarning)

def load_portfolio(filename: str) -> Dict[str, Any]:
    """Load portfolio data from a JSON or YAML file"""
    if not os.path.exists(filename):
        print(f"Error: Portfolio file {filename} not found.")
        sys.exit(1)
        
    if filename.endswith('.json'):
        with open(filename, 'r') as f:
            return json.load(f)
    elif filename.endswith(('.yaml', '.yml')):
        with open(filename, 'r') as f:
            return yaml.safe_load(f)
    else:
        print("Error: Portfolio file must be .json, .yaml, or .yml")
        sys.exit(1)

def load_preferences(filename: str) -> Dict[str, Any]:
    """Load preferences data from a JSON or YAML file"""
    if not os.path.exists(filename):
        print(f"Error: Preferences file {filename} not found.")
        sys.exit(1)
        
    if filename.endswith('.json'):
        with open(filename, 'r') as f:
            return json.load(f)
    elif filename.endswith(('.yaml', '.yml')):
        with open(filename, 'r') as f:
            return yaml.safe_load(f)
    else:
        print("Error: Preferences file must be .json, .yaml, or .yml")
        sys.exit(1)

def save_output(data: Dict[str, Any], filename: str = None):
    """Save analysis output to a file"""
    if not filename:
        # Generate filename with current date
        today = datetime.now().strftime('%Y-%m-%d')
        filename = f"market_analysis_{today}.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Analysis saved to {filename}")

async def run_analysis(portfolio_file: str, preferences_file: str, output_file: str = None):
    """Run the market sentiment analysis"""
    print("Loading portfolio and preferences...")
    portfolio = load_portfolio(portfolio_file)
    preferences = load_preferences(preferences_file)
    
    print("Starting market sentiment analysis...")
    flow = MarketSentimentFlow(portfolio, preferences)
    results = {}
    
    async for event in flow.stream_analysis():
        # Parse the event
        event_str = event.replace("data: ", "").strip()
        if event_str:
            try:
                event_data = json.loads(event_str)
                
                # Display progress
                if event_data.get("type") == "status":
                    print(f"Status: {event_data.get('message')}")
                
                # Store completed task data
                if event_data.get("type") == "task_complete":
                    task_name = event_data.get("task")
                    print(f"Completed: {task_name}")
                    results[task_name] = event_data.get("data")
                
                # Handle errors
                if event_data.get("type") == "error":
                    print(f"Error: {event_data.get('message')}")
                
                # Handle completion
                if event_data.get("type") == "complete":
                    print(f"Analysis complete: {event_data.get('message')}")
                    
            except json.JSONDecodeError:
                print(f"Warning: Could not parse event: {event_str[:50]}...")
    
    # Save the results
    if results and output_file:
        save_output(results, output_file)
    elif results:
        save_output(results)
    
    # Extract and display recommendations
    if "recommendations" in results:
        print("\n=== TRADING RECOMMENDATIONS ===")
        recommendations = results["recommendations"]
        if "trading_recommendations" in recommendations:
            for rec in recommendations["trading_recommendations"]:
                action = rec.get("action", "").upper()
                ticker = rec.get("ticker", "")
                company = rec.get("company", "")
                confidence = rec.get("confidence", "")
                print(f"{action} {ticker} ({company}) - Confidence: {confidence}")
        
        if "summary" in recommendations:
            print("\nSummary:")
            print(recommendations["summary"])
    
    return results

def main():
    """Command line interface for market sentiment analysis"""
    parser = argparse.ArgumentParser(description="Market Sentiment Analysis CLI")
    parser.add_argument("--portfolio", "-p", required=True, help="Path to portfolio JSON or YAML file")
    parser.add_argument("--preferences", "-pref", required=True, help="Path to preferences JSON or YAML file")
    parser.add_argument("--output", "-o", help="Output file path (optional)")
    
    args = parser.parse_args()
    
    asyncio.run(run_analysis(args.portfolio, args.preferences, args.output))

if __name__ == "__main__":
    main()