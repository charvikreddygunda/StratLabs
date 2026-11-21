def run_backtest(data, starting_cash):
    """Simulate trading on the Position signals. Adds a Portfolio_Value column with the total value each day."""
    cash = starting_cash
    shares = 0
    portfolio_values = []

    # Use yesterday's signal so we only trade on information we'd actually have had (avoids look-ahead bias).
    for price, signal in zip(data["Close"], data["Position"].shift(1)):
        if signal == 1 and shares == 0:
            # Only whole shares can be bought, so any leftover cash stays uninvested.
            shares = cash // price
            cash -= shares * price
        elif signal == 0 and shares > 0:
            cash += shares * price
            shares = 0

        portfolio_values.append(cash + shares * price)

    data["Portfolio_Value"] = portfolio_values
    return data


def run_buy_and_hold(data, starting_cash):
    """Buy as many whole shares as possible on day 1 and hold. Adds a BuyHold_Value column."""
    first_price = data["Close"].iloc[0]
    shares = starting_cash // first_price
    leftover_cash = starting_cash - (shares * first_price)
    data["BuyHold_Value"] = leftover_cash + shares * data["Close"]
    return data