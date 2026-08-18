import streamlit as st
import pandas as pd
import plotly.express as px

from src.data import get_single_stock
from src.analysis import calculate_metrics


# PAGE CONFIGURATION

st.set_page_config(
    page_title="StockScope",
    page_icon="📈",
    layout="wide"
)


# HEADER

st.title("📈 StockScope")

st.markdown(
    """
    **Stock Performance & Risk Analytics**

    Compare stocks using historical performance, volatility,
    Sharpe ratio, drawdown, and correlation.
    """
)

# SIDEBAR

st.sidebar.header("Dashboard Settings")

available_tickers = [
    # Technology
    "AAPL",
    "MSFT",
    "NVDA",
    "GOOGL",
    "META",
    "AMZN",
    "AVGO",
    "ORCL",
    "ADBE",
    "CRM",
    "AMD",
    "INTC",
    "CSCO",
    "QCOM",
    "IBM",

    # Consumer
    "TSLA",
    "NFLX",
    "NKE",
    "MCD",
    "SBUX",
    "KO",
    "PEP",
    "WMT",
    "COST",

    # Financial
    "JPM",
    "BAC",
    "GS",
    "MS",
    "V",
    "MA",
    "BLK",
    "C",

    # Healthcare
    "LLY",
    "JNJ",
    "PFE",
    "MRK",
    "ABBV",
    "UNH",

    # Energy
    "XOM",
    "CVX",
    "COP",

    # Industrial
    "CAT",
    "GE",
    "HON",
    "BA",
    "UPS",
    "RTX",

    # Communication
    "DIS",
    "CMCSA",
    "T",
    "VZ",

    # ETFs / Benchmarks
    "SPY",
    "QQQ",
    "DIA",
    "IWM",
]


tickers = st.sidebar.multiselect(
    "Select stocks",
    available_tickers,
    default=[
        "AAPL",
        "MSFT",
        "NVDA"
    ]
)


period = st.sidebar.selectbox(
    "Time period",
    [
        "1mo",
        "3mo",
        "6mo",
        "1y",
        "2y",
        "5y"
    ],
    index=3
)


benchmark = st.sidebar.selectbox(
    "Benchmark",
    [
        "SPY",
        "QQQ",
        "DIA",
        "IWM"
    ]
)


# ==================================================
# VALIDATE STOCK SELECTION
# ==================================================

if not tickers:

    st.warning(
        "Please select at least one stock."
    )

    st.stop()

# LOAD STOCK DATA

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

    st.error(
        "No stock data could be loaded."
    )

    st.stop()


# LOAD BENCHMARK

try:

    benchmark_data = get_single_stock(
        benchmark,
        period
    )

except Exception:

    benchmark_data = pd.DataFrame()


# CALCULATE METRICS

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

# PORTFOLIO OVERVIEW

st.header("📊 Portfolio Overview")


best_stock = metrics_df.loc[
    metrics_df["Return (%)"].idxmax()
]


worst_stock = metrics_df.loc[
    metrics_df["Return (%)"].idxmin()
]


average_return = metrics_df[
    "Return (%)"
].mean()


average_volatility = metrics_df[
    "Volatility (%)"
].mean()


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

# PERFORMANCE COMPARISON

st.header("📈 Performance Comparison")


normalized_data = pd.DataFrame()


for ticker, data in stock_data.items():

    prices = data["Close"]

    normalized_prices = (
        prices / prices.iloc[0]
    ) * 100

    normalized_data[ticker] = normalized_prices


# Add benchmark

if not benchmark_data.empty:

    benchmark_prices = benchmark_data["Close"]

    benchmark_normalized = (
        benchmark_prices /
        benchmark_prices.iloc[0]
    ) * 100

    normalized_data[benchmark] = (
        benchmark_normalized
    )


normalized_data = normalized_data.dropna()


fig_performance = px.line(
    normalized_data,
    x=normalized_data.index,
    y=normalized_data.columns,
    title="Normalized Performance",
    labels={
        "value": "Growth of 100",
        "Date": "Date",
        "variable": "Asset"
    }
)


fig_performance.update_layout(
    hovermode="x unified"
)


st.plotly_chart(
    fig_performance,
    use_container_width=True
)


st.caption(
    "All assets are normalized to 100 at the beginning "
    "of the selected period."
)

# PERFORMANCE & RISK METRICS

st.header("📋 Performance & Risk Metrics")


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

        metrics_display[column] = (
            metrics_display[column]
            .round(2)
        )


metrics_display = metrics_display.sort_values(
    "Return (%)",
    ascending=False
)


st.dataframe(
    metrics_display,
    use_container_width=True,
    hide_index=True
)


# STOCK RANKING

st.header("🏆 Stock Ranking")


ranking = metrics_df.copy()


ranking["Rank"] = (
    ranking["Return (%)"]
    .rank(
        ascending=False,
        method="min"
    )
    .astype(int)
)


ranking = ranking.sort_values(
    "Rank"
)


ranking_columns = [
    "Rank",
    "Ticker",
    "Return (%)",
    "Volatility (%)",
    "Sharpe Ratio",
    "Max Drawdown (%)"
]


st.dataframe(
    ranking[ranking_columns],
    use_container_width=True,
    hide_index=True
)

# RISK VS RETURN

st.header("⚖️ Risk vs Return")


risk_return = metrics_df.copy()


fig_risk = px.scatter(
    risk_return,
    x="Volatility (%)",
    y="Return (%)",
    text="Ticker",
    size="Average Volume",
    title="Risk vs Return",
    labels={
        "Volatility (%)":
            "Annualized Volatility (%)",
        "Return (%)":
            "Return (%)"
    }
)


fig_risk.update_traces(
    textposition="top center"
)


st.plotly_chart(
    fig_risk,
    use_container_width=True
)


st.caption(
    "Higher volatility means greater historical price variability."
)


# CORRELATION

st.header("🔗 Stock Correlation")


returns = pd.DataFrame()


for ticker, data in stock_data.items():

    returns[ticker] = (
        data["Close"]
        .pct_change()
    )


correlation = returns.corr()


fig_corr = px.imshow(
    correlation,
    text_auto=".2f",
    title="Daily Return Correlation",
    labels={
        "color": "Correlation"
    }
)


st.plotly_chart(
    fig_corr,
    use_container_width=True
)


st.caption(
    "Values closer to 1 indicate stronger positive correlation."
)


# INDIVIDUAL STOCK ANALYSIS

st.header("🔍 Individual Stock Analysis")


selected_stock = st.selectbox(
    "Select a stock",
    list(stock_data.keys())
)


selected_data = stock_data[
    selected_stock
].copy()


selected_metrics = metrics_df[
    metrics_df["Ticker"] == selected_stock
].iloc[0]

# STOCK SUMMARY


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

# MOVING AVERAGES

selected_data["MA20"] = (
    selected_data["Close"]
    .rolling(20)
    .mean()
)


selected_data["MA50"] = (
    selected_data["Close"]
    .rolling(50)
    .mean()
)

# PRICE CHART

st.subheader(
    f"{selected_stock} Price & Moving Averages"
)


price_chart = selected_data[
    [
        "Close",
        "MA20",
        "MA50"
    ]
].reset_index()


fig_price = px.line(
    price_chart,
    x="Date",
    y=[
        "Close",
        "MA20",
        "MA50"
    ],
    title=f"{selected_stock} Price & Moving Averages",
    labels={
        "value": "Price",
        "variable": "Indicator"
    }
)


fig_price.update_layout(
    hovermode="x unified"
)


st.plotly_chart(
    fig_price,
    use_container_width=True
)

# TRADING VOLUME

st.subheader(
    f"{selected_stock} Trading Volume"
)


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


# MAXIMUM DRAWDOWN

st.subheader(
    f"{selected_stock} Drawdown"
)


running_max = (
    selected_data["Close"]
    .cummax()
)


drawdown = (
    (
        selected_data["Close"]
        - running_max
    )
    / running_max
    * 100
)


drawdown_df = pd.DataFrame(
    {
        "Drawdown (%)": drawdown
    }
)


fig_drawdown = px.area(
    drawdown_df,
    x=drawdown_df.index,
    y="Drawdown (%)",
    title=f"{selected_stock} Drawdown",
    labels={
        "Drawdown (%)":
            "Drawdown (%)"
    }
)


st.plotly_chart(
    fig_drawdown,
    use_container_width=True
)

# ROLLING VOLATILITY

st.subheader(
    f"{selected_stock} 30-Day Rolling Volatility"
)


selected_data["Daily Return"] = (
    selected_data["Close"]
    .pct_change()
)


selected_data["Rolling Volatility"] = (
    selected_data["Daily Return"]
    .rolling(30)
    .std()
    * (252 ** 0.5)
    * 100
)


fig_volatility = px.line(
    selected_data,
    x=selected_data.index,
    y="Rolling Volatility",
    title=(
        f"{selected_stock} "
        "30-Day Rolling Volatility"
    ),
    labels={
        "Rolling Volatility":
            "Annualized Volatility (%)",
        "Date":
            "Date"
    }
)


fig_volatility.update_layout(
    hovermode="x unified"
)


st.plotly_chart(
    fig_volatility,
    use_container_width=True
)

# SIMPLE ANALYTICAL INTERPRETATION

st.header("💡 Analytics Summary")


sharpe = selected_metrics[
    "Sharpe Ratio"
]


drawdown_value = selected_metrics[
    "Max Drawdown (%)"
]


if sharpe > 1:

    st.success(
        "The stock showed strong "
        "risk-adjusted performance during "
        "the selected period."
    )

elif sharpe > 0:

    st.info(
        "The stock showed positive "
        "risk-adjusted performance during "
        "the selected period."
    )

else:

    st.warning(
        "The stock showed negative "
        "risk-adjusted performance during "
        "the selected period."
    )


if drawdown_value < -30:

    st.warning(
        f"The stock experienced a significant "
        f"maximum drawdown of "
        f"{drawdown_value:.2f}% during the "
        "selected period."
    )

# FOOTER

st.divider()


st.caption(
    """
    StockScope is an educational financial analytics tool.
    Market data may be delayed. The analysis is not investment advice.
    """
)
