import plotly.graph_objects as go


def price_chart(data):
    """Price with both moving averages, plus markers on the days the strategy bought and sold."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Daily price", line=dict(color="gray")))
    fig.add_trace(go.Scatter(x=data.index, y=data["Short_MA"], name="20-day average"))
    fig.add_trace(go.Scatter(x=data.index, y=data["Long_MA"], name="50-day average"))

    # The backtester trades the day AFTER the averages cross (to avoid look-ahead bias),
    # so the buy and sell markers go on that next day too. That way the chart matches the real trades.
    trades = data["Position"].shift(1).diff()
    buys = data[trades == 1]
    sells = data[trades == -1]
    fig.add_trace(go.Scatter(x=buys.index, y=buys["Close"], mode="markers", name="Buy",
                             marker=dict(symbol="triangle-up", size=12, color="green")))
    fig.add_trace(go.Scatter(x=sells.index, y=sells["Close"], mode="markers", name="Sell",
                             marker=dict(symbol="triangle-down", size=12, color="red")))

    fig.update_layout(yaxis_title="Price per share ($)", hovermode="x unified")
    return fig


def portfolio_chart(data):
    """Compare the strategy's portfolio value with buy-and-hold over time."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data["Portfolio_Value"], name="Follow the trend"))
    fig.add_trace(go.Scatter(x=data.index, y=data["BuyHold_Value"], name="Buy and hold",
                             line=dict(dash="dash")))
    fig.update_layout(yaxis_title="Value of your money ($)", hovermode="x unified")
    return fig