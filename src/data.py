import yfinance as yf
import pandas as pd


def get_stock_data(tickers, period="1y"):
    data = yf.download(
        tickers,
        period=period,
        auto_adjust=True,
        progress=False
    )

    return data


def get_single_stock(ticker, period="1y"):
    stock = yf.Ticker(ticker)

    data = stock.history(period=period)

    data.index = pd.to_datetime(data.index)

    return data