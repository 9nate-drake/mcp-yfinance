# yfinance MCP Server

A Model Context Protocol server that provides financial data using yfinance (Yahoo Finance api)

## Installation

### Requirements
- Python 3.10 or higher
- Claude Desktop

### Steps

1. Install required packages:
```bash
pip install mcp yfinance
```

## Configuration

Add to your Claude Desktop config file (on Windows this is at %APPDATA%/Claude/claude_desktop_config.json) :

### Windows
```json
{
  "mcpServers": {
    "yfinance": {
      "command": "python",
      "args": [
        "C:/path/to/finance_server/server.py"
      ]
    }
  }
}
```

### macOS/Linux
```json
{
  "mcpServers": {
    "yfinance": {
      "command": "python",
      "args": [
        "/path/to/finance_server/server.py"
      ]
    }
  }
}
```

Replace the path with the actual full path to your server.py file.

## Usage

1. Restart Claude Desktop
2. Look for the yfinance server in the 🔌 menu
3. Example queries:
   - Get current stock info: "Get me the current stock information for MSFT"
   - Get historical data: "Get me AAPL's historical data for the last 3 months using get_historical_data"

## Development

To modify the server:
1. Edit server.py directly
2. Restart Claude Desktop to apply changes