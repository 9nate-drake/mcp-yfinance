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

async def fetch_stock_info(symbol: str) -> dict[str, Any]:
    """Fetch current stock information."""
    stock = yf.Ticker(symbol)
    info = stock.info
    
    return {
        "symbol": symbol,
        "price": info.get("currentPrice"),
        "volume": info.get("volume"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("forwardPE"),
        "dividend_yield": info.get("dividendYield"),
        "timestamp": datetime.now().isoformat()
    }

app = Server("yfinance-server")

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
                "required": ["symbol"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls for historical data."""
    if name != "get_historical_data":
        raise ValueError(f"Unknown tool: {name}")

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