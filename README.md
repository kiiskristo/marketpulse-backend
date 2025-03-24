# Market Sentiment Analysis System

An automated system that analyzes financial news, market data, and influencer statements to provide personalized trading recommendations based on market sentiment.

## Features

- **Multi-Agent Architecture**: Leverages crewAI to orchestrate specialized agents for different aspects of market analysis
- **Daily Sentiment Analysis**: Collects and analyzes global financial news, company-specific developments, and key influencer statements
- **Portfolio-Aware Recommendations**: Generates trading recommendations tailored to user's portfolio and preferences
- **Caching System**: Efficiently reuses API responses to minimize costs
- **API & CLI Interfaces**: Access via RESTful API or command line

## Setup Instructions

### 1. Install Dependencies

```bash
# Clone the repository
git clone https://github.com/yourusername/market-sentiment.git
cd market-sentiment

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy the environment template
cp .env.template .env

# Edit .env and add your API keys
# You'll need:
# - OpenAI API key
# - Bing Search API key
# - Alpha Vantage API key
```

### 3. Create Portfolio and Preferences Files

See examples in the `examples/` directory:
- `portfolio.json`: Your stock holdings
- `preferences.json`: Your investment preferences

### 4. Running the Application

#### Via CLI:

```bash
# Run a one-time analysis
python -m src.market_sentiment.cli --portfolio examples/portfolio.json --preferences examples/preferences.json --output analysis.json
```

#### As a Web Service:

```bash
# Start the API server
python app.py

# The API will be available at:
# http://localhost:8000/api/sentiment/analyze (POST)
# http://localhost:8000/api/sentiment/demo (GET)
```

## API Usage

### Analyze Portfolio Sentiment

```bash
curl -X POST http://localhost:8000/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d @examples/request.json
```

Where `request.json` contains:

```json
{
  "portfolio": {
    "holdings": [
      {"ticker": "AAPL", "company": "Apple Inc.", "allocation": 15, "sector": "Technology"}
    ]
  },
  "preferences": {
    "risk_tolerance": "moderate",
    "preferred_sectors": ["Technology"],
    "preferred_regions": ["US"],
    "investment_horizon": "medium-term"
  }
}
```

## Deployment

The application is designed to be deployed on Railway or similar platforms:

```bash
# Deploy to Railway
railway up
```

## Cost Optimization

The system uses several cost-optimization strategies:

1. **Intelligent Caching**: API responses are cached to avoid redundant calls
2. **Shared Global Analysis**: Market-wide data is shared among all users
3. **GPT-4o-mini**: Uses efficient LLM to minimize token costs
4. **Scheduled Execution**: Runs only during market days

## Future Enhancements

- Interactive Brokers integration for automated trading
- Email delivery of daily recommendations
- User dashboard for tracking recommendation performance
- Custom news source integrations