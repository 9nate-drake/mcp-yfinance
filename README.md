# yfinance MCP Server

A Model Context Protocol server that provides financial data to Claude Desktop using yfinance (Yahoo Finance api).
Most code created by Claude.

## Installation

### Requirements
- Python 3.10 or higher
- Claude Desktop

### Install

1. Clone this repo:
```bash
git clone https://github.com/9nate-drake/mcp-yfinance
```   
2. Install required packages:
```bash
pip install mcp yfinance
```

## Configuration

Add to your Claude Desktop config file claude_desktop_config.json (on Windows this is usually at %APPDATA%/Claude/):

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
   - Get current stock price: "Get me the current stock price for MSFT"
   - Get historical data: "Analyse the last 3 months of Apple stock performance"
   - Check ownership: "What's the intsitutional ownership of Nvidia?"
   - Check analyst targets: "What's the median price target for TSLA?"

## Development

To modify the server:
1. Edit server.py directly
2. Restart Claude Desktop to apply changes

## TODO
~~* Add complete range of yfinance functions~~
* Check compliance with anthropic recommended practice for mcp servers
