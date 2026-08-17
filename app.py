import streamlit as st
import pandas as pd
import plotly.express as px

from src.data import get_single_stock
from src.analysis import calculate_metrics


st.set_page_config(
    page_title="StockScope",
    page_icon="📈",
    layout="wide"
)


st.title("📈 StockScope")

st.markdown(
    "A simple dashboard for monitoring and comparing stock performance."
)


# Sidebar
st.sidebar.header("Settings")

tickers = st.sidebar.multiselect(
    "Select stocks",
    [
        "AAPL",
        "MSFT",
        "NVDA",
        "GOOGL",
        "AMZN",
        "TSLA",
        "META",
        "NFLX"
    ],
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
        "5y"
    ],
    index=3
)


if not tickers:

    st.warning("Select at least one stock.")

    st.stop()


# Load data
stock_data = {}

for ticker in tickers:

    try:
        stock_data[ticker] = get_single_stock(
            ticker,
            period
        )

    except Exception as e:

        st.error(f"Could not load {ticker}: {e}")


# Performance comparison

st.header("Performance Comparison")


normalized_data = pd.DataFrame()


for ticker, data in stock_data.items():

    prices = data["Close"]

    normalized = (prices / prices.iloc[0]) * 100

    normalized_data[ticker] = normalized


normalized_data = normalized_data.dropna()


fig = px.line(
    normalized_data,
    x=normalized_data.index,
    y=normalized_data.columns,
    title="Normalized Stock Performance",
    labels={
        "value": "Value",
        "Date": "Date",
        "variable": "Stock"
    }
)

fig.update_layout(
    hovermode="x unified"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# Metrics

st.header("Stock Metrics")


metrics = []

for ticker, data in stock_data.items():

    metrics.append(
        calculate_metrics(
            ticker,
            data
        )
    )


metrics_df = pd.DataFrame(metrics)

# KPI Cards
best_stock = metrics_df.loc[
    metrics_df["Return (%)"].idxmax()
]

worst_stock = metrics_df.loc[
    metrics_df["Return (%)"].idxmin()
]

avg_return = metrics_df["Return (%)"].mean()

avg_volatility = metrics_df["Volatility (%)"].mean()


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
        f"{avg_return:.2f}%"
    )

with col4:
    st.metric(
        "Average Volatility",
        f"{avg_volatility:.2f}%"
    )
# Volume

st.header("Trading Volume")


fig_volume = px.bar(
    data,
    x=data.index,
    y="Volume",
    title=f"{selected_stock} Trading Volume"
)


st.plotly_chart(
    fig_volume,
    use_container_width=True
)

# Risk vs Return

st.header("Risk vs Return")

risk_return = metrics_df.copy()

fig_risk = px.scatter(
    risk_return,
    x="Volatility (%)",
    y="Return (%)",
    text="Ticker",
    size="Average Volume",
    title="Risk vs Return"
)

fig_risk.update_traces(
    textposition="top center"
)

st.plotly_chart(
    fig_risk,
    use_container_width=True
)