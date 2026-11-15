"""Offline tests: yfinance is mocked so these run without network access."""
import sys
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app as app_module  # noqa: E402
from utils import get_data  # noqa: E402

INFO = {
    "regularMarketPreviousClose": 100.0, "currentPrice": 105.0, "volume": 12_345_678,
    "marketCap": 2_500_000_000_000, "longName": "Example Corp", "symbol": "EXM",
    "fiftyTwoWeekHigh": 120.5, "fiftyTwoWeekLow": 80.25, "trailingPE": 25.123,
}


def _ohlc(multiindex: bool, ticker="EXM", n=5):
    idx = pd.date_range("2026-11-02", periods=n, freq="D")
    fields = {k: np.linspace(100, 110, n) for k in ("Open", "High", "Low", "Close", "Adj Close")}
    fields["Volume"] = np.arange(n) * 1000
    df = pd.DataFrame(fields, index=idx)
    if multiindex:  # shape newer yfinance returns by default
        df.columns = pd.MultiIndex.from_product([df.columns, [ticker]], names=["Price", "Ticker"])
    return df


@pytest.fixture()
def client():
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


@pytest.mark.parametrize("multiindex", [True, False])
def test_ohlc_columns_flattened(multiindex):
    with mock.patch.object(get_data.yf, "download", return_value=_ohlc(multiindex)):
        data = get_data.get_ohlc_data("EXM", "1mo")
    assert list(data.columns[:4]) == ["Open", "High", "Low", "Close"]
    assert isinstance(data["Close"], pd.Series)


def test_fetch_stock_data_formats_metrics():
    with mock.patch.object(get_data.yf, "Ticker") as t:
        t.return_value.info = dict(INFO)
        out = get_data.fetch_stock_data("EXM")
    assert out["change"] == "+5.0"
    assert out["volume"] == "12.35M"
    assert {"name": "Market Cap", "value": "$2.5 Trillion"} in out["metrics"]


def test_flat_day_and_missing_pe_dont_crash():
    info = dict(INFO, currentPrice=100.0)
    info.pop("trailingPE")
    with mock.patch.object(get_data.yf, "Ticker") as t:
        t.return_value.info = info
        out = get_data.fetch_stock_data("EXM")  # used to raise UnboundLocalError
    assert out["change"] == "0.0"
    assert {"name": "PE Ratio", "value": "N/A"} in out["metrics"]


def test_verify_ticker():
    with mock.patch.object(get_data.yf, "download", return_value=_ohlc(True)):
        assert get_data.verify_ticker("EXM") is True
    with mock.patch.object(get_data.yf, "download", return_value=pd.DataFrame()):
        assert get_data.verify_ticker("NOPE") is False
    assert get_data.verify_ticker("") is False


def test_full_flow_renders_stock_page(client):
    with mock.patch.object(get_data.yf, "download", return_value=_ohlc(True)), \
         mock.patch.object(get_data.yf, "Ticker") as t:
        t.return_value.info = dict(INFO)
        assert client.get("/").status_code == 200
        r = client.post("/confirm_ticker", json={"ticker": "EXM"})
        assert r.get_json() == {"validity": True}
        r = client.post("/get_stock_data", json={
            "mainTicker": "EXM", "chartType": "candlestick", "compare": False,
            "comparisonTicker": "", "range": "1mo",
        })
        assert r.status_code == 302
        page = client.get(r.headers["Location"])
        assert page.status_code == 200
        assert b"Example Corp" in page.data
        assert client.get("/dash/primary/").status_code == 200


def test_no_wildcard_cors_and_debug_off(client):
    r = client.get("/", headers={"Origin": "https://evil.example"})
    assert "Access-Control-Allow-Origin" not in r.headers
    assert app_module.app.debug is False
