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

metrics_df = metrics_df.sort_values(
    "Return (%)",
    ascending=False
)


st.dataframe(
    metrics_df,
    use_container_width=True,
    hide_index=True
)


# Individual stock

st.header("Stock Price")


selected_stock = st.selectbox(
    "Choose a stock",
    tickers
)


data = stock_data[selected_stock]


fig_price = px.line(
    data,
    x=data.index,
    y="Close",
    title=f"{selected_stock} Price"
)


fig_price.update_layout(
    xaxis_title="Date",
    yaxis_title="Price"
)


st.plotly_chart(
    fig_price,
    use_container_width=True
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