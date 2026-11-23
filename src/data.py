import yfinance as yf


def get_stock_data(ticker, start_date, end_date):
    """Download daily price data for one ticker. Raises ValueError if nothing comes back."""
    data = yf.download(ticker, start=start_date, end=end_date,
                       progress=False, multi_level_index=False)

    # yfinance doesn't raise an error for a bad ticker; it returns an empty table,
    # so we check here before bad data reaches the strategy code.
    if data.empty:
        raise ValueError(f"No data found for {ticker} between {start_date} and {end_date}")
    return data

# Big companies on the dropdown for beginner users since they wouldn't know tickers.
POPULAR_COMPANIES = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Nvidia": "NVDA",
    "Tesla": "TSLA",
    "Netflix": "NFLX",
    "Disney": "DIS",
    "Nike": "NKE",
    "Coca-Cola": "KO",
    "McDonald's": "MCD",
    "Walmart": "WMT",
}

def get_company_name(ticker):
    """Look up a company's full name for display. Falls back to the ticker if the lookup fails."""
    # This is only for display, so if Yahoo is slow or doesn't return a name,
    # the app should keep going with the ticker instead of crashing.
    try:
        return yf.Ticker(ticker).info.get("longName", ticker)
    except Exception:
        return ticker