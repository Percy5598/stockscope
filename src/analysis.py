import numpy as np
import pandas as pd


def calculate_return(data):
    """
    Calculate total percentage return
    over the selected period.
    """

    if data.empty or len(data) < 2:
        return np.nan

    start_price = data["Close"].iloc[0]
    end_price = data["Close"].iloc[-1]

    return (
        (end_price / start_price) - 1
    ) * 100


def calculate_volatility(data):
    """
    Calculate annualized historical volatility.

    Uses daily returns and assumes
    252 trading days per year.
    """

    if data.empty or len(data) < 2:
        return np.nan

    returns = (
        data["Close"]
        .pct_change()
        .dropna()
    )

    if returns.empty:
        return np.nan

    volatility = (
        returns.std()
        * np.sqrt(252)
        * 100
    )

    return volatility


def calculate_sharpe_ratio(
    data,
    risk_free_rate=0.02
):
    """
    Calculate annualized Sharpe ratio.

    risk_free_rate:
        Annual risk-free rate.
        Default = 2%.
    """

    if data.empty or len(data) < 2:
        return np.nan

    returns = (
        data["Close"]
        .pct_change()
        .dropna()
    )

    if returns.empty:
        return np.nan

    annual_return = (
        returns.mean() * 252
    )

    annual_volatility = (
        returns.std()
        * np.sqrt(252)
    )

    if annual_volatility == 0:
        return np.nan

    sharpe_ratio = (
        annual_return - risk_free_rate
    ) / annual_volatility

    return sharpe_ratio


def calculate_max_drawdown(data):
    """
    Calculate the maximum historical
    drawdown from a previous peak.
    """

    if data.empty:
        return np.nan

    prices = data["Close"]

    running_max = prices.cummax()

    drawdown = (
        (prices - running_max)
        / running_max
    )

    return drawdown.min() * 100


def calculate_average_volume(data):
    """
    Calculate average daily trading volume.
    """

    if data.empty:
        return np.nan

    return data["Volume"].mean()


def calculate_metrics(ticker, data):
    """
    Calculate all major performance and
    risk metrics for a stock.
    """

    if data.empty:
        return {
            "Ticker": ticker,
            "Current Price": np.nan,
            "Return (%)": np.nan,
            "Volatility (%)": np.nan,
            "Sharpe Ratio": np.nan,
            "Max Drawdown (%)": np.nan,
            "Average Volume": np.nan,
        }

    return {
        "Ticker": ticker,

        "Current Price": data[
            "Close"
        ].iloc[-1],

        "Return (%)": calculate_return(
            data
        ),

        "Volatility (%)": calculate_volatility(
            data
        ),

        "Sharpe Ratio": calculate_sharpe_ratio(
            data
        ),

        "Max Drawdown (%)": calculate_max_drawdown(
            data
        ),

        "Average Volume": calculate_average_volume(
            data
        ),
    }


def calculate_daily_returns(data):
    """
    Return a pandas Series containing
    daily percentage returns.
    """

    if data.empty:
        return pd.Series(dtype=float)

    return (
        data["Close"]
        .pct_change()
        .dropna()
    )


def calculate_rolling_volatility(
    data,
    window=30
):
    """
    Calculate annualized rolling volatility.

    Default window = 30 trading days.
    """

    returns = calculate_daily_returns(
        data
    )

    if returns.empty:
        return pd.Series(dtype=float)

    return (
        returns
        .rolling(window)
        .std()
        * np.sqrt(252)
        * 100
    )


def calculate_drawdown_series(data):
    """
    Calculate the complete historical
    drawdown series.
    """

    if data.empty:
        return pd.Series(dtype=float)

    prices = data["Close"]

    running_max = prices.cummax()

    drawdown = (
        (prices - running_max)
        / running_max
        * 100
    )

    return drawdown