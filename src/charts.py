import plotly.graph_objects as go


def price_chart(data):
    """Price with both moving averages, plus markers on the days the strategy bought and sold."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Price", line=dict(color="gray")))
    fig.add_trace(go.Scatter(x=data.index, y=data["Short_MA"], name="Short average (20 days)"))
    fig.add_trace(go.Scatter(x=data.index, y=data["Long_MA"], name="Long average (50 days)"))

    # Trades happen the day AFTER the signal changes (see run_backtest), so mark those days.
    trades = data["Position"].shift(1).diff()
    buys = data[trades == 1]
    sells = data[trades == -1]
    fig.add_trace(go.Scatter(x=buys.index, y=buys["Close"], mode="markers", name="Buy",
                             marker=dict(symbol="triangle-up", size=12, color="green")))
    fig.add_trace(go.Scatter(x=sells.index, y=sells["Close"], mode="markers", name="Sell",
                             marker=dict(symbol="triangle-down", size=12, color="red")))

    fig.update_layout(yaxis_title="Price ($)", hovermode="x unified")
    return fig


def portfolio_chart(data):
    """Compare the strategy's portfolio value with buy-and-hold over time."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data["Portfolio_Value"], name="Strategy"))
    fig.add_trace(go.Scatter(x=data.index, y=data["BuyHold_Value"], name="Buy-and-hold",
                             line=dict(dash="dash")))
    fig.update_layout(yaxis_title="Portfolio value ($)", hovermode="x unified")
    return fig