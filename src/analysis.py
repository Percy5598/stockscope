import pandas as pd
import numpy as np


def calculate_return(data):

    if data.empty:
        return np.nan

    start_price = data["Close"].iloc[0]
    end_price = data["Close"].iloc[-1]

    return ((end_price / start_price) - 1) * 100


def calculate_volatility(data):

    returns = data["Close"].pct_change()

    volatility = returns.std() * np.sqrt(252) * 100

    return volatility


def calculate_metrics(ticker, data):

    return {
        "Ticker": ticker,
        "Current Price": data["Close"].iloc[-1],
        "Return (%)": calculate_return(data),
        "Volatility (%)": calculate_volatility(data),
        "Average Volume": data["Volume"].mean()
    }