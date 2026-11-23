from datetime import date, timedelta

import streamlit as st

from backtest import run_backtest, run_buy_and_hold
from charts import portfolio_chart, price_chart
from data import get_stock_data
from metrics import annual_volatility, max_drawdown, total_return
from strategy import calculate_moving_averages, generate_signals

SHORT_WINDOW = 20
LONG_WINDOW = 50

st.set_page_config(page_title="StrategyLab", layout="wide")
st.title("StrategyLab")
st.write("Backtest a moving-average strategy against buy-and-hold.")

st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Stock ticker", "AAPL")
# Default to the last two years so the app always shows recent data,
# and so there's enough history after the 50-day average warms up.
start_date = st.sidebar.date_input("Start date", date.today() - timedelta(days=730))
end_date = st.sidebar.date_input("End date", date.today())
starting_cash = st.sidebar.number_input("Starting cash ($)", min_value=100, value=10000, step=1000)
run_clicked = st.sidebar.button("Run backtest")

if run_clicked:
    # Users may type extra spaces or lowercase letters, so clean the ticker first.
    ticker = ticker.strip().upper()
    if not ticker:
        st.error("Please enter a stock ticker, like AAPL or MSFT.")
        st.stop()

    try:
        data = get_stock_data(ticker, start_date, end_date)
    except ValueError as error:
        st.error(str(error))
        st.stop()

    # The backtester only buys whole shares, so with less cash than one share
    # it would never trade and the results would look broken.
    first_price = data["Close"].iloc[0]
    if starting_cash < first_price:
        st.error(f"Starting cash must be at least one share's price (${first_price:,.2f}).")
        st.stop()

    data = calculate_moving_averages(data, SHORT_WINDOW, LONG_WINDOW)
    data = generate_signals(data)
    data = run_backtest(data, starting_cash)
    data = run_buy_and_hold(data, starting_cash)

    strategy_return = total_return(data["Portfolio_Value"])
    hold_return = total_return(data["BuyHold_Value"])
    gap = abs(strategy_return - hold_return) * 100
    if strategy_return > hold_return:
        st.success(f"The strategy beat buy-and-hold on {ticker} by {gap:.1f} percentage points.")
    else:
        st.info(f"Buy-and-hold beat the strategy on {ticker} by {gap:.1f} percentage points.")

    strategy_col, hold_col = st.columns(2)
    with strategy_col:
        st.subheader("Strategy")
        st.metric("Total return", f"{strategy_return:.1%}")
        st.metric("Volatility", f"{annual_volatility(data['Portfolio_Value']):.1%}")
        st.metric("Max drawdown", f"{max_drawdown(data['Portfolio_Value']):.1%}")
    with hold_col:
        st.subheader("Buy-and-hold")
        st.metric("Total return", f"{hold_return:.1%}")
        st.metric("Volatility", f"{annual_volatility(data['BuyHold_Value']):.1%}")
        st.metric("Max drawdown", f"{max_drawdown(data['BuyHold_Value']):.1%}")

    st.subheader(f"{ticker} price and trades")
    st.plotly_chart(price_chart(data))

    st.subheader("Portfolio value over time")
    st.plotly_chart(portfolio_chart(data))