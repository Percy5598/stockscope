import streamlit as st
import pandas as pd
import plotly.express as px

from src.data import get_single_stock
from src.analysis import calculate_metrics


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="StockScope",
    page_icon="📈",
    layout="wide"
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("📈 StockScope")

st.markdown(
    """
    **Stock Performance & Risk Analytics**

    Compare stocks using historical performance, volatility,
    Sharpe ratio, and maximum drawdown.
    """
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.header("Dashboard Settings")

available_tickers = [
    # Technology
    "AAPL",      # Apple
    "MSFT",      # Microsoft
    "NVDA",      # NVIDIA
    "GOOGL",     # Alphabet
    "META",      # Meta
    "AMZN",      # Amazon
    "AVGO",      # Broadcom
    "ORCL",      # Oracle
    "ADBE",      # Adobe
    "CRM",       # Salesforce
    "AMD",       # AMD
    "INTC",      # Intel
    "CSCO",      # Cisco
    "QCOM",      # Qualcomm
    "IBM",       # IBM

    # Consumer
    "TSLA",      # Tesla
    "NFLX",      # Netflix
    "NKE",       # Nike
    "MCD",       # McDonald's
    "SBUX",      # Starbucks
    "KO",        # Coca-Cola
    "PEP",       # PepsiCo
    "WMT",       # Walmart
    "COST",      # Costco

    # Financial
    "JPM",       # JPMorgan Chase
    "BAC",       # Bank of America
    "GS",        # Goldman Sachs
    "MS",        # Morgan Stanley
    "V",         # Visa
    "MA",        # Mastercard
    "BLK",       # BlackRock
    "C",         # Citigroup

    # Healthcare
    "LLY",       # Eli Lilly
    "JNJ",       # Johnson & Johnson
    "PFE",       # Pfizer
    "MRK",       # Merck
    "ABBV",      # AbbVie
    "UNH",       # UnitedHealth

    # Energy
    "XOM",       # Exxon Mobil
    "CVX",       # Chevron
    "COP",       # ConocoPhillips

    # Industrial
    "CAT",       # Caterpillar
    "GE",        # GE Aerospace
    "HON",       # Honeywell
    "BA",        # Boeing
    "UPS",       # UPS
    "RTX",       # RTX

    # Communication
    "DIS",       # Disney
    "CMCSA",     # Comcast
    "T",         # AT&T
    "VZ",        # Verizon

    # ETFs / Benchmarks
    "SPY",       # S&P 500
    "QQQ",       # Nasdaq 100
    "DIA",       # Dow Jones
    "IWM",       # Russell 2000
]

tickers = st.sidebar.multiselect(
    "Select stocks",
    available_tickers,
    default=["AAPL", "MSFT", "NVDA"]
)

period = st.sidebar.selectbox(
    "Time period",
    [
        "1mo",
        "3mo",
        "6mo",
        "1y",
        "2y",
        "5y",
    ],
    index=3
)


# --------------------------------------------------
# Validate selection
# --------------------------------------------------

if not tickers:

    st.warning("Please select at least one stock.")

    st.stop()


# --------------------------------------------------
# Load data
# --------------------------------------------------

stock_data = {}

with st.spinner("Loading market data..."):

    for ticker in tickers:

        try:

            data = get_single_stock(
                ticker,
                period
            )

            if not data.empty:
                stock_data[ticker] = data

        except Exception as error:

            st.error(
                f"Could not load {ticker}: {error}"
            )


if not stock_data:

    st.error("No stock data could be loaded.")

    st.stop()


# --------------------------------------------------
# Calculate metrics
# --------------------------------------------------

metrics = []

for ticker, data in stock_data.items():

    try:

        metrics.append(
            calculate_metrics(
                ticker,
                data
            )
        )

    except Exception as error:

        st.error(
            f"Could not calculate metrics for {ticker}: {error}"
        )


metrics_df = pd.DataFrame(metrics)


# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------

st.header("Portfolio Overview")

best_stock = metrics_df.loc[
    metrics_df["Return (%)"].idxmax()
]

worst_stock = metrics_df.loc[
    metrics_df["Return (%)"].idxmin()
]

average_return = metrics_df["Return (%)"].mean()

average_volatility = metrics_df["Volatility (%)"].mean()


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Best Performer",
        best_stock["Ticker"],
        f'{best_stock["Return (%)"]:.2f}%'
    )


with col2:

    st.metric(
        "Worst Performer",
        worst_stock["Ticker"],
        f'{worst_stock["Return (%)"]:.2f}%'
    )


with col3:

    st.metric(
        "Average Return",
        f"{average_return:.2f}%"
    )


with col4:

    st.metric(
        "Average Volatility",
        f"{average_volatility:.2f}%"
    )


# --------------------------------------------------
# Performance Comparison
# --------------------------------------------------

st.header("Performance Comparison")

normalized_data = pd.DataFrame()


for ticker, data in stock_data.items():

    prices = data["Close"]

    normalized_prices = (
        prices / prices.iloc[0]
    ) * 100

    normalized_data[ticker] = normalized_prices


normalized_data = normalized_data.dropna()


fig_performance = px.line(
    normalized_data,
    x=normalized_data.index,
    y=normalized_data.columns,
    title="Normalized Performance",
    labels={
        "value": "Growth of €100",
        "Date": "Date",
        "variable": "Stock"
    }
)


fig_performance.update_layout(
    hovermode="x unified",
    legend_title="Stock"
)


st.plotly_chart(
    fig_performance,
    use_container_width=True
)


st.caption(
    "All stocks are normalized to 100 at the beginning of the selected period."
)


# --------------------------------------------------
# Metrics Table
# --------------------------------------------------

st.header("Performance & Risk Metrics")


metrics_display = metrics_df.copy()


numeric_columns = [
    "Current Price",
    "Return (%)",
    "Volatility (%)",
    "Sharpe Ratio",
    "Max Drawdown (%)",
    "Average Volume"
]


for column in numeric_columns:

    if column in metrics_display.columns:

        metrics_display[column] = metrics_display[column].round(2)


metrics_display = metrics_display.sort_values(
    "Return (%)",
    ascending=False
)


st.dataframe(
    metrics_display,
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# Risk vs Return
# --------------------------------------------------

st.header("Risk vs Return")

risk_return = metrics_df.copy()


fig_risk = px.scatter(
    risk_return,
    x="Volatility (%)",
    y="Return (%)",
    text="Ticker",
    size="Average Volume",
    title="Risk vs Return",
    labels={
        "Volatility (%)": "Annualized Volatility (%)",
        "Return (%)": "Return (%)"
    }
)


fig_risk.update_traces(
    textposition="top center"
)


fig_risk.update_layout(
    hovermode="closest"
)


st.plotly_chart(
    fig_risk,
    use_container_width=True
)


st.caption(
    "Stocks further right have higher volatility. "
    "Stocks higher up have higher returns."
)


# --------------------------------------------------
# Individual Stock Analysis
# --------------------------------------------------

st.header("Individual Stock Analysis")


selected_stock = st.selectbox(
    "Select a stock",
    list(stock_data.keys())
)


selected_data = stock_data[selected_stock]


# --------------------------------------------------
# Stock summary
# --------------------------------------------------

selected_metrics = metrics_df[
    metrics_df["Ticker"] == selected_stock
].iloc[0]


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Current Price",
        f'{selected_metrics["Current Price"]:.2f}'
    )


with col2:

    st.metric(
        "Return",
        f'{selected_metrics["Return (%)"]:.2f}%'
    )


with col3:

    st.metric(
        "Volatility",
        f'{selected_metrics["Volatility (%)"]:.2f}%'
    )


with col4:

    st.metric(
        "Sharpe Ratio",
        f'{selected_metrics["Sharpe Ratio"]:.2f}'
    )


# --------------------------------------------------
# Price Chart
# --------------------------------------------------

st.subheader(f"{selected_stock} Price")


fig_price = px.line(
    selected_data,
    x=selected_data.index,
    y="Close",
    title=f"{selected_stock} Closing Price",
    labels={
        "Close": "Price",
        "Date": "Date"
    }
)


fig_price.update_layout(
    hovermode="x unified"
)


st.plotly_chart(
    fig_price,
    use_container_width=True
)


# --------------------------------------------------
# Volume Chart
# --------------------------------------------------

st.subheader(f"{selected_stock} Trading Volume")


fig_volume = px.bar(
    selected_data,
    x=selected_data.index,
    y="Volume",
    title=f"{selected_stock} Trading Volume",
    labels={
        "Volume": "Volume",
        "Date": "Date"
    }
)


st.plotly_chart(
    fig_volume,
    use_container_width=True
)


# --------------------------------------------------
# Drawdown Chart
# --------------------------------------------------

st.subheader(f"{selected_stock} Drawdown")


running_max = selected_data["Close"].cummax()

drawdown = (
    selected_data["Close"] - running_max
) / running_max * 100


drawdown_df = pd.DataFrame(
    {
        "Drawdown (%)": drawdown
    }
)


fig_drawdown = px.area(
    drawdown_df,
    x=drawdown_df.index,
    y="Drawdown (%)",
    title=f"{selected_stock} Drawdown"
)


fig_drawdown.update_layout(
    yaxis_title="Drawdown (%)",
    xaxis_title="Date"
)


st.plotly_chart(
    fig_drawdown,
    use_container_width=True
)


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "StockScope is an educational analytics tool. "
    "Market data may be delayed and should not be considered investment advice."
)