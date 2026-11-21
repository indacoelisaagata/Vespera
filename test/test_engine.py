from datetime import datetime, timedelta

import numpy as np
import pytest

from engine import (
    DEPRECIATION_BY_CATEGORY,
    ETF_HOLDINGS,
    compute_portfolio_xray,
    hours_remaining,
    recommend_rebalance,
    simulate_opportunity_cost,
    simulate_return_scenarios,
)


def test_single_etf_exposure_matches_holdings():
    xray = compute_portfolio_xray({"CSSPX (S&P 500)": 1000.0})
    apple = xray["exposures"].set_index("Asset").loc["Apple", "Exposure (%)"]
    assert apple == pytest.approx(ETF_HOLDINGS["CSSPX (S&P 500)"]["Apple"])


def test_hhi_matches_manual_computation():
    holdings = ETF_HOLDINGS["CSSPX (S&P 500)"]
    expected = sum((v / 100) ** 2 for k, v in holdings.items() if not k.startswith("Other"))
    xray = compute_portfolio_xray({"CSSPX (S&P 500)": 500.0})
    assert xray["hhi"] == pytest.approx(expected, abs=1e-5)


def test_empty_portfolio_is_handled():
    xray = compute_portfolio_xray({"SWDA (MSCI World)": 0.0})
    assert xray["total"] == 0.0 and xray["hhi"] == 0.0


def test_rebalance_does_not_increase_concentration():
    portfolio = {"IUIT (S&P 500 Info Tech)": 5000.0}
    result = recommend_rebalance(portfolio, 1000.0)
    assert result["recommended_etf"] != "IUIT (S&P 500 Info Tech)"
    assert result["new_hhi"] < result["current_hhi"]


def test_scenarios_are_ordered():
    df = simulate_return_scenarios(100.0, years=5)
    last = df.iloc[-1]
    assert last["Low"] < last["Base"] < last["High"]


def test_category_depreciation_is_used():
    beauty = simulate_opportunity_cost(100.0, category="Beauty & Skincare").iloc[-1]
    fashion = simulate_opportunity_cost(100.0, category="Fashion").iloc[-1]
    assert beauty["Residual Item Value (€)"] < fashion["Residual Item Value (€)"]
    assert set(DEPRECIATION_BY_CATEGORY) >= {"Fashion", "Beauty & Skincare"}


def test_hours_remaining_counts_down_and_stops_at_zero():
    start = datetime(2026, 1, 1, 12, 0)
    assert hours_remaining(start, 72, now=start + timedelta(hours=18)) == pytest.approx(54)
    assert hours_remaining(start, 72, now=start + timedelta(hours=100)) == 0.0
