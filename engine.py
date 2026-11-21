from datetime import datetime

import numpy as np
import pandas as pd

COOLING_OFF_HOURS = 72

# Illustrative data: top holdings entered manually and rounded. Not live market data.
ETF_DATA_NOTE = (
    "ETF holdings are illustrative, approximate and manually entered. "
    "Check current data on the issuer's website before drawing conclusions."
)

# Assumed annual loss of resale value by category (illustrative assumptions, not market data).
DEPRECIATION_BY_CATEGORY = {
    "Fashion": 0.30,
    "Beauty & Skincare": 0.90,  # consumable: value disappears quickly
    "Tech & Gadgets": 0.40,
    "Lifestyle": 0.35,
}
DEFAULT_DEPRECIATION = 0.35

# Illustrative return scenarios (annual). They are NOT forecasts.
RETURN_SCENARIOS = {"Low": 0.035, "Base": 0.075, "High": 0.10}

ETF_HOLDINGS = {
    "SWDA (MSCI World)": {
        "Apple": 5.1, "Microsoft": 4.6, "Nvidia": 4.4, "Amazon": 2.7,
        "Meta": 1.8, "Alphabet": 2.8, "Broadcom": 1.2, "Tesla": 1.0,
        "JPMorgan": 0.9, "Eli Lilly": 1.1, "Others": 74.4
    },
    "CSSPX (S&P 500)": {
        "Apple": 7.1, "Microsoft": 6.5, "Nvidia": 6.2, "Amazon": 3.8,
        "Meta": 2.5, "Alphabet": 3.9, "Broadcom": 1.6, "Tesla": 1.4,
        "JPMorgan": 1.3, "Eli Lilly": 1.5, "Other USA": 64.2
    },
    "IUIT (S&P 500 Info Tech)": {
        "Apple": 21.5, "Microsoft": 20.2, "Nvidia": 19.8, "Broadcom": 5.1,
        "Salesforce": 2.8, "Oracle": 2.6, "Adobe": 2.4, "AMD": 2.3,
        "Other Tech": 23.3
    },
    "EIMI (MSCI Emerging Markets)": {
        "TSMC": 9.2, "Tencent": 4.1, "Samsung": 3.8, "Alibaba": 2.4,
        "Reliance": 1.4, "HDFC Bank": 1.3, "Meituan": 1.2,
        "Other Emerging": 76.6
    }
}


def compute_portfolio_xray(allocations: dict[str, float]) -> dict:
    """Look-through exposure of a portfolio of ETFs and its concentration (HHI).

    Assumptions (kept explicit on purpose):
    - HHI is computed only on the named single stocks listed in ETF_HOLDINGS.
      Residual buckets ("Others", "Other USA", ...) are treated as made of many
      tiny positions, so they contribute roughly zero to HHI.
    - Each ETF lists a different number of named holdings, so comparing HHI
      across ETFs partly reflects how much detail the data contains.
    - The diversification score 100 * exp(-18 * HHI) is a simplified indicator
      chosen for readability, not a standard risk measure. It ignores
      correlations, sectors, countries and costs.
    """
    total_value = sum(allocations.values())
    if total_value <= 0:
        return {"exposures": pd.DataFrame(), "single_stocks": pd.DataFrame(), "hhi": 0.0, "score": 0, "total": 0.0}

    weights = {etf: val / total_value for etf, val in allocations.items()}
    aggregated_exposure = {}

    for etf, w in weights.items():
        holdings = ETF_HOLDINGS.get(etf, {})
        for company, pct in holdings.items():
            # Real underlying exposure (%) across the total portfolio
            real_pct = w * pct
            aggregated_exposure[company] = aggregated_exposure.get(company, 0.0) + real_pct

    df_exp = (
        pd.DataFrame(list(aggregated_exposure.items()), columns=["Asset", "Exposure (%)"])
        .sort_values(by="Exposure (%)", ascending=False)
        .reset_index(drop=True)
    )

    # Filter out residual buckets ("Others", "Other USA", etc.) before computing HHI
    single_stocks = df_exp[~df_exp["Asset"].str.startswith("Other")]
    hhi = float(np.sum((single_stocks["Exposure (%)"] / 100.0) ** 2))

    raw_score = 100 * np.exp(-18 * hhi)
    div_score = int(np.clip(round(raw_score), 5, 99))

    return {
        "exposures": df_exp,
        "single_stocks": single_stocks,
        "hhi": round(hhi, 5),
        "score": div_score,
        "total": total_value
    }


def recommend_rebalance(allocations: dict[str, float], saved_amount: float) -> dict:
    current_stats = compute_portfolio_xray(allocations)
    best_etf = None
    best_hhi = float("inf")
    best_score = current_stats["score"]

    for candidate_etf in ETF_HOLDINGS.keys():
        simulated = allocations.copy()
        simulated[candidate_etf] = simulated.get(candidate_etf, 0.0) + saved_amount
        sim_stats = compute_portfolio_xray(simulated)

        if sim_stats["hhi"] < best_hhi:
            best_hhi = sim_stats["hhi"]
            best_etf = candidate_etf
            best_score = sim_stats["score"]

    return {
        "recommended_etf": best_etf,
        "current_hhi": current_stats["hhi"],
        "new_hhi": best_hhi,
        "current_score": current_stats["score"],
        "new_score": best_score,
        "score_delta": best_score - current_stats["score"]
    }


def simulate_opportunity_cost(
    amount: float,
    years: int = 5,
    annual_return: float = 0.075,
    depreciation_rate: float | None = None,
    category: str | None = None,
) -> pd.DataFrame:
    """Compare the invested amount with the residual value of the purchased item.

    If depreciation_rate is not given, it is taken from the item's category.
    """
    if depreciation_rate is None:
        depreciation_rate = DEPRECIATION_BY_CATEGORY.get(category, DEFAULT_DEPRECIATION)

    months = np.arange(0, years * 12 + 1)
    t_years = months / 12.0

    invested_curve = amount * ((1 + annual_return) ** t_years)
    # Instant 20% post-purchase value drop + annual depreciation
    item_value_curve = (amount * 0.80) * ((1 - depreciation_rate) ** t_years)

    return pd.DataFrame({
        "Years": t_years,
        "Invested Capital (€)": np.round(invested_curve, 2),
        "Residual Item Value (€)": np.round(item_value_curve, 2),
    })


def simulate_return_scenarios(
    amount: float,
    years: int = 5,
    scenarios: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Value of the invested amount under several illustrative return scenarios."""
    scenarios = scenarios or RETURN_SCENARIOS
    t_years = np.arange(0, years * 12 + 1) / 12.0
    data = {"Years": t_years}
    for name, rate in scenarios.items():
        data[name] = np.round(amount * ((1 + rate) ** t_years), 2)
    return pd.DataFrame(data)


def hours_remaining(
    created_at: datetime,
    total_hours: float = COOLING_OFF_HOURS,
    now: datetime | None = None,
) -> float:
    """Hours left in a cooling-off contract, based on its real start time."""
    now = now or datetime.now()
    elapsed = (now - created_at).total_seconds() / 3600.0
    return max(0.0, total_hours - elapsed)
