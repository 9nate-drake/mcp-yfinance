import os
import json
import logging
from datetime import datetime
from typing import Any, Sequence
from collections.abc import Sequence as SequenceABC

import yfinance as yf
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
from pydantic import AnyUrl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yfinance-server")

# Default settings
DEFAULT_SYMBOL = "AAPL"

app = Server("yfinance-server")

async def fetch_stock_info(symbol: str) -> dict[str, Any]:
    """Fetch current stock information."""
    stock = yf.Ticker(symbol)
    info = stock.info
    return info
    
@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available financial resources."""
    uri = AnyUrl(f"finance://{DEFAULT_SYMBOL}/info")
    return [
        Resource(
            uri=uri,
            name=f"Current stock information for {DEFAULT_SYMBOL}",
            mimeType="application/json",
            description="Real-time stock market data"
        )
    ]

@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read current stock information."""
    symbol = DEFAULT_SYMBOL
    if str(uri).startswith("finance://") and str(uri).endswith("/info"):
        symbol = str(uri).split("/")[-2]
    else:
        raise ValueError(f"Unknown resource: {uri}")

    try:
        stock_data = await fetch_stock_info(symbol)
        return json.dumps(stock_data, indent=2)
    except Exception as e:
        raise RuntimeError(f"Stock API error: {str(e)}")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available financial tools."""
    return [
        Tool(
            name="get_historical_data",
            description="Get historical stock data for a symbol",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol"
                    },
                    "period": {
                        "type": "string",
                        "description": "Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)",
                        "enum": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
                    }
                },
                "required": ["symbol", "metric"]
            }
        ),
        Tool(
            name="get_stock_metric",
            description="""Get a specific metric for a stock using yfinance field names.
            Common requests and their exact field names:
            
            Stock Price & Trading Info:
            - Current/Stock Price: currentPrice
            - Opening Price: open
            - Day's High: dayHigh
            - Day's Low: dayLow
            - Previous Close: previousClose
            - 52 Week High: fiftyTwoWeekHigh
            - 52 Week Low: fiftyTwoWeekLow
            - 50 Day Average: fiftyDayAverage
            - 200 Day Average: twoHundredDayAverage
            - Trading Volume: volume
            - Average Volume: averageVolume
            - Average Daily Volume (10 day): averageDailyVolume10Day
            - Market Cap/Capitalization: marketCap
            - Beta: beta
            - Bid Price: bid
            - Ask Price: ask
            - Bid Size: bidSize
            - Ask Size: askSize
            
            Company Information:
            - Company Name: longName
            - Short Name: shortName
            - Business Description/About/Summary: longBusinessSummary
            - Industry: industry
            - Sector: sector
            - Website: website
            - Number of Employees: fullTimeEmployees
            - Country: country
            - State: state
            - City: city
            - Address: address1
            
            Financial Metrics:
            - PE Ratio: trailingPE
            - Forward PE: forwardPE
            - Price to Book: priceToBook
            - Price to Sales: priceToSalesTrailing12Months
            - Enterprise Value: enterpriseValue
            - Enterprise to EBITDA: enterpriseToEbitda
            - Enterprise to Revenue: enterpriseToRevenue
            - Book Value: bookValue
            
            Earnings & Revenue:
            - Revenue/Total Revenue: totalRevenue
            - Revenue Growth: revenueGrowth
            - Revenue Per Share: revenuePerShare
            - EBITDA: ebitda
            - EBITDA Margins: ebitdaMargins
            - Net Income: netIncomeToCommon
            - Earnings Growth: earningsGrowth
            - Quarterly Earnings Growth: earningsQuarterlyGrowth
            - Forward EPS: forwardEps
            - Trailing EPS: trailingEps
            
            Margins & Returns:
            - Profit Margin: profitMargins
            - Operating Margin: operatingMargins
            - Gross Margins: grossMargins
            - Return on Equity/ROE: returnOnEquity
            - Return on Assets/ROA: returnOnAssets
            
            Dividends:
            - Dividend Yield: dividendYield
            - Dividend Rate: dividendRate
            - Dividend Date: lastDividendDate
            - Ex-Dividend Date: exDividendDate
            - Payout Ratio: payoutRatio
            
            Balance Sheet:
            - Total Cash: totalCash
            - Cash Per Share: totalCashPerShare
            - Total Debt: totalDebt
            - Debt to Equity: debtToEquity
            - Current Ratio: currentRatio
            - Quick Ratio: quickRatio
            
            Ownership:
            - Institutional Ownership: heldPercentInstitutions
            - Insider Ownership: heldPercentInsiders
            - Float Shares: floatShares
            - Shares Outstanding: sharesOutstanding
            - Short Ratio: shortRatio
            
            Analyst Coverage:
            - Analyst Recommendation: recommendationKey
            - Number of Analysts: numberOfAnalystOpinions
            - Price Target Mean: targetMeanPrice
            - Price Target High: targetHighPrice
            - Price Target Low: targetLowPrice
            - Price Target Median: targetMedianPrice
            
            Risk Metrics:
            - Overall Risk: overallRisk
            - Audit Risk: auditRisk
            - Board Risk: boardRisk
            - Compensation Risk: compensationRisk
            
            Other:
            - Currency: currency
            - Exchange: exchange
            - Year Change/52 Week Change: 52WeekChange
            - S&P 500 Year Change: SandP52WeekChange""",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol"
                    },
                    "metric": {
                        "type": "string",
                        "description": "The metric to retrieve, use camelCase"
                    }
                },
                "required": ["symbol", "metric"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls."""
    if name == "get_stock_metric":
        symbol = arguments["symbol"]
        metric = arguments["metric"]
        
        try:
            stock_data = await fetch_stock_info(symbol)
            if metric in stock_data:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({metric: stock_data[metric]}, indent=2)
                    )
                ]
            else:
                raise ValueError(f"Metric {metric} not found")
        except Exception as e:
            logger.error(f"Stock API error: {str(e)}")
            raise RuntimeError(f"Stock API error: {str(e)}")
            
    elif name == "get_historical_data":

        if not isinstance(arguments, dict) or "symbol" not in arguments:
            raise ValueError("Invalid arguments")

        symbol = arguments["symbol"]
        period = arguments.get("period", "1mo")

        try:
            stock = yf.Ticker(symbol)
            history = stock.history(period=period)
            
            data = []
            for date, row in history.iterrows():
                data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": row["Open"],
                    "high": row["High"],
                    "low": row["Low"],
                    "close": row["Close"],
                    "volume": row["Volume"]
                })

            return [
                TextContent(
                    type="text",
                    text=json.dumps(data, indent=2)
                )
            ]
        except Exception as e:
            logger.error(f"Stock API error: {str(e)}")
            raise RuntimeError(f"Stock API error: {str(e)}")

async def main():
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())