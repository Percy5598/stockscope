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

def calculate_sharpe_ratio(data, risk_free_rate=0.02):

    returns = data["Close"].pct_change().dropna()

    annual_return = returns.mean() * 252

    annual_volatility = returns.std() * (252 ** 0.5)

    if annual_volatility == 0:
        return 0

    return (
        annual_return - risk_free_rate
    ) / annual_volatility

def calculate_metrics(ticker, data):

    return {
        "Ticker": ticker,
        "Current Price": data["Close"].iloc[-1],
        "Return (%)": calculate_return(data),
        "Volatility (%)": calculate_volatility(data),
        "Sharpe Ratio": calculate_sharpe_ratio(data),
        "Average Volume": data["Volume"].mean()
    }