import numpy as np
import pandas as pd

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


def simulate_opportunity_cost(amount: float, years: int = 5, annual_return: float = 0.075, depreciation_rate: float = 0.35) -> pd.DataFrame:
    months = np.arange(0, years * 12 + 1)
    t_years = months / 12.0

    invested_curve = amount * ((1 + annual_return) ** t_years)
    # Instant 20% post-purchase value drop + annual depreciation
    item_value_curve = (amount * 0.80) * ((1 - depreciation_rate) ** t_years)

    return pd.DataFrame({
        "Years": t_years,
        "Invested Capital (€)": np.round(invested_curve, 2),
        "Residual Item Value (€)": np.round(item_value_curve, 2)
    })
