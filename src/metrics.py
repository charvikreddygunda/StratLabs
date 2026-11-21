def total_return(values):
    """Return the overall gain or loss as a decimal (0.25 means +25%)."""
    return values.iloc[-1] / values.iloc[0] - 1

def annual_volatility(values):
    """Return how much the value swings, as a yearly decimal (0.20 means 20%)."""
    daily_returns = values.pct_change()
    # There are about 252 trading days in a year; multiplying by sqrt(252)
    # turns daily volatility into a yearly figure that's easier to compare.
    return daily_returns.std() * (252 ** 0.5)

def max_drawdown(values):
    """Return the largest drop from a previous peak, as a negative decimal (-0.20 means -20%)."""
    running_peak = values.cummax()
    drawdowns = values / running_peak - 1
    return drawdowns.min()