from datetime import date, timedelta

import streamlit as st

from backtest import run_backtest, run_buy_and_hold
from charts import portfolio_chart, price_chart
from data import POPULAR_COMPANIES, get_company_name, get_stock_data
from metrics import annual_volatility, max_drawdown, total_return
from strategy import calculate_moving_averages, generate_signals

# Keeping these fixed for the MVP. Letting users pick their own windows
# is on my Schedule list for later.
SHORT_WINDOW = 20
LONG_WINDOW = 50

# Shown when you hover over the ⓘ next to each number.
RETURN_HELP = "How much your money grew or shrank overall. $10,000 becoming $12,000 is a +20% return."
VOLATILITY_HELP = "How bumpy the ride was. Higher means bigger ups and downs from day to day."
DRAWDOWN_HELP = "The worst drop from a high point. If your money hit $15,000 and then fell to $12,000, that's -20%."

st.set_page_config(page_title="StrategyLab", page_icon="📈", layout="wide")
st.title("📈 StrategyLab")
st.write("See what would have happened if you had followed a simple trading rule, "
         "compared with just buying a stock and holding it.")

with st.expander("New to investing? Start here"):
    st.markdown("""
**How the rule works**
1. We look at two averages of the stock's price: the last **20 days** (short-term) and the last **50 days** (long-term).
2. When the short-term average goes **above** the long-term one, prices have been rising, so we **buy**.
3. When it goes **below**, prices have been falling, so we **sell** and keep our money as cash.
4. We compare that with **buy and hold**: buying on day one and never selling.

**Words you'll see**
- **Stock / share:** a tiny piece of ownership in a company.
- **Ticker:** a short code for a company's stock, like AAPL for Apple.
- **In cash:** you don't own any shares, so stock price changes don't affect your money.
- **Moving average:** the average price over the last few days. It smooths out daily jumps.
- **Backtest:** testing a rule on past prices. It shows what *would have* happened, not what will happen.
""")

st.sidebar.header("Settings")
company = st.sidebar.selectbox("Company", list(POPULAR_COMPANIES) + ["Other"])
if company == "Other":
    ticker = st.sidebar.text_input(
        "Stock ticker",
        help="A short code for a company's stock, like AAPL for Apple or F for Ford. "
             "Not sure? Search the company name plus 'stock ticker' online.")
    company_name = None
else:
    ticker = POPULAR_COMPANIES[company]
    company_name = company

# Two years back by default. One year felt too short since the 50-day
# average eats up the first couple months before any trades can happen.
start_date = st.sidebar.date_input("Start date", date.today() - timedelta(days=730))
end_date = st.sidebar.date_input("End date", date.today())
starting_cash = st.sidebar.number_input("Starting cash ($)", min_value=100, value=10000, step=1000)
run_clicked = st.sidebar.button("Run backtest", type="primary")

if run_clicked:
    # People might type "aapl" or add a space by accident, so clean it up first.
    ticker = ticker.strip().upper()
    if not ticker:
        st.error("Please enter a stock ticker, like AAPL or MSFT.")
        st.stop()

    # st.stop() ends the page right here, so nothing below tries to run on bad data.
    try:
        data = get_stock_data(ticker, start_date, end_date)
    except ValueError as error:
        st.error(str(error))
        st.stop()

    # Only look up the name for "Other" tickers. The popular ones already have a name.
    if company_name is None:
        company_name = get_company_name(ticker)

    # The backtester only buys whole shares. If you can't afford even one,
    # it never trades and the results just look broken, so catch it early.
    first_price = data["Close"].iloc[0]
    if starting_cash < first_price:
        st.error(f"Starting cash must be at least one share's price (${first_price:,.2f}).")
        st.stop()

    data = calculate_moving_averages(data, SHORT_WINDOW, LONG_WINDOW)
    data = generate_signals(data)
    data = run_backtest(data, starting_cash)
    data = run_buy_and_hold(data, starting_cash)

    strategy_end = data["Portfolio_Value"].iloc[-1]
    hold_end = data["BuyHold_Value"].iloc[-1]

    st.divider()
    st.subheader(f"What happened to your ${starting_cash:,.0f} in {company_name} ({ticker})?")
    st.write(f"**Following the trend:** ${starting_cash:,.0f} → ${strategy_end:,.0f}")
    st.write(f"**Buying and holding:** ${starting_cash:,.0f} → ${hold_end:,.0f}")

    # Saying one approach "made more" is misleading if both lost money, so call that out first.
    if strategy_end < starting_cash and hold_end < starting_cash:
        st.warning(f"Both approaches lost money on {company_name} during this period.")

    if strategy_end > hold_end:
        st.success(f"Following the trend ended ${strategy_end - hold_end:,.0f} ahead of buying and holding.")
    else:
        st.info(f"Buying and holding ended ${hold_end - strategy_end:,.0f} ahead of following the trend.")

    strategy_col, hold_col = st.columns(2)
    with strategy_col:
        st.subheader("Follow the trend")
        st.metric("Total return", f"{total_return(data['Portfolio_Value']):.1%}", help=RETURN_HELP)
        st.metric("Volatility", f"{annual_volatility(data['Portfolio_Value']):.1%}", help=VOLATILITY_HELP)
        st.metric("Max drawdown", f"{max_drawdown(data['Portfolio_Value']):.1%}", help=DRAWDOWN_HELP)
    with hold_col:
        st.subheader("Buy and hold")
        st.metric("Total return", f"{total_return(data['BuyHold_Value']):.1%}", help=RETURN_HELP)
        st.metric("Volatility", f"{annual_volatility(data['BuyHold_Value']):.1%}", help=VOLATILITY_HELP)
        st.metric("Max drawdown", f"{max_drawdown(data['BuyHold_Value']):.1%}", help=DRAWDOWN_HELP)

    st.divider()
    st.subheader(f"{company_name} price and trades")
    st.plotly_chart(price_chart(data))
    st.caption("Gray is the daily price. The two colored lines are the 20-day and 50-day averages. "
               "A green ▲ is a buy and a red ▼ is a sell. Each one happens right after the two averages cross.")

    st.divider()
    st.subheader("Your money over time")
    st.plotly_chart(portfolio_chart(data))
    st.caption("The solid line follows the trend, and the dashed line buys and holds. "
               "Flat parts of the solid line are times the rule was sitting in cash.")