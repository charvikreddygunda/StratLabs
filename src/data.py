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