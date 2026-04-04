# AI Coding Guidelines for Market Pulse Project

## Project Overview
This is a Python script (`market_pulse.py`) that generates daily Hong Kong stock market summaries by fetching data from Yahoo Finance and displaying top 10 market winners and losers.

## Architecture
- **Single-file application**: All logic in `market_pulse.py` with functions for data fetching, processing, and display
- **Data flow**: Hardcoded HK ticker list → yfinance API calls → sort by %change → formatted console output
- **External dependencies**: `yfinance` library for Yahoo Finance integration

## Key Patterns
- **HK stock tickers**: Always include `.HK` suffix for yfinance API calls (e.g., `"0001.HK"`), but display symbols without suffix
- **Data structure**: Use dictionaries with keys: `symbol`, `name`, `price`, `change`, `change_percent`, `volume`
- **Error handling**: Wrap individual stock fetches in try-except, skip failures silently to continue processing
- **Formatting**: Fixed-width console tables using f-strings with alignment specifiers (`:<8`, `:>10.2f`)
- **Price display**: Prefix with `HK$` and format to 2 decimal places
- **Change indicators**: Add `+` prefix for positive values in change and %change columns

## Development Workflow
- **Run script**: `python3 market_pulse.py` (requires `yfinance` installed via `pip install yfinance`)
- **Data validation**: Check `regularMarketPrice` exists and is not None before processing stock info
- **Sorting logic**: Use `sorted()` with `key=lambda x: x['change_percent']` for losers (ascending), reverse slice for winners
- **Name truncation**: Limit to 23 chars + ".." if longer than 25 chars for table display

## Code Style
- **Imports**: Standard library first (`datetime`, `sys`), then third-party (`yfinance`)
- **Function structure**: `get_hk_stocks()` returns ticker list, `fetch_stock_data()` processes all tickers, `display_summary()` handles output
- **Constants**: Hardcode ticker list as array in `get_hk_stocks()` (covers major Hang Seng components)
- **Exit handling**: Use `sys.exit(1)` with error message if no data retrieved

## Common Modifications
- **Add stocks**: Append new `.HK` tickers to the list in `get_hk_stocks()`
- **Change display**: Modify f-string formats in `display_summary()` for different column widths
- **Add metrics**: Extend stock dict in `fetch_stock_data()` with additional yfinance info fields
- **Error reporting**: Replace silent skips with logging for debugging failed fetches