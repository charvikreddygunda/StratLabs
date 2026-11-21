def calculate_moving_averages(data, short_window, long_window):
    """Add short and long moving averages of the Close price. Raises ValueError if the windows are invalid."""

    # Equal windows are blocked too as then the two averages would be identical lines,
    # so they'd never cross and the strategy would never trade.
    if short_window >= long_window:
        raise ValueError("Invalid window sizes: short_window must be less than long_window.")

    # The first rows will be NaN because a moving average needs a full window of past prices.
    # That's expected, and it means the strategy can't trade on those early days.
    data["Short_MA"] = data["Close"].rolling(window=short_window).mean()
    data["Long_MA"] = data["Close"].rolling(window=long_window).mean()
    return data