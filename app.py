import html
from datetime import datetime, timedelta

import streamlit as st
import plotly.graph_objects as go
from engine import (
    COOLING_OFF_HOURS,
    ETF_DATA_NOTE,
    ETF_HOLDINGS,
    RETURN_SCENARIOS,
    compute_portfolio_xray,
    hours_remaining,
    recommend_rebalance,
    simulate_opportunity_cost,
    simulate_return_scenarios,
)

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="vespera — Behavioral & Quantitative Wealth",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- DESIGN SYSTEM CSS INJECTION (QUIET LUXURY / ALL-OUTFIT) ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap');

    :root {
        --bg-primary: #FAF8F9;
        --surface: #FFFFFF;
        --border-subtle: #EAE2E6;
        --text-primary: #1E161A;
        --text-secondary: #685860;
        --accent-plum: #8A244E;
        --accent-coral: #D9534F;
    }

    html, body, [class*="css"], .stApp, p, span, label, div, input, select, button, li {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-style: normal !important;
        color: var(--text-primary);
    }

    .stApp {
        background-color: var(--bg-primary) !important;
    }

    /* Hide default Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Headings & Subtitles */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        font-family: 'Outfit', sans-serif !important;
        color: #1E161A !important;
        font-weight: 600 !important;
        font-size: 1.22rem !important;
        letter-spacing: -0.015em !important;
        margin-bottom: 0.2rem !important;
    }
    .stCaption, [data-testid="stCaptionContainer"] p {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 400 !important;
        color: #685860 !important;
        font-size: 0.88rem !important;
    }

    /* Brand Header */
    .vespera-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.1rem 1.6rem;
        background-color: #FFFFFF;
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        margin-bottom: 1.8rem;
        box-shadow: 0 2px 12px rgba(30, 22, 26, 0.03);
    }
    .vespera-logo {
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.85rem;
        font-weight: 700;
        letter-spacing: -0.035em;
        color: #8A244E !important;
    }
    .vespera-badge {
        font-family: 'Outfit', sans-serif !important;
        background-color: #F6EEF2;
        color: #8A244E !important;
        font-size: 0.74rem;
        font-weight: 600;
        padding: 0.4rem 0.9rem;
        border-radius: 999px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        border: 1px solid #E5D4DC;
    }

    /* KPI Cards */
    .v-card {
        background-color: var(--surface);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 1.45rem 1.55rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 14px rgba(30, 22, 26, 0.025);
    }
    .v-label {
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #75646C !important;
        margin-bottom: 0.4rem;
        font-weight: 600;
    }
    .v-metric {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E161A !important;
        letter-spacing: -0.025em;
        line-height: 1.15;
    }
    .v-sub {
        font-size: 0.85rem;
        color: #685860 !important;
        margin-top: 0.4rem;
    }

    /* Form Container & Unified Clean Inputs */
    [data-testid="stForm"] {
        background-color: #FFFFFF !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 14px rgba(30, 22, 26, 0.025);
    }
    [data-testid="stWidgetLabel"] p {
        color: #1E161A !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }

    /* Outer wrapper for text, number, and selectbox */
    [data-testid="stTextInputRootElement"],
    [data-testid="stNumberInputContainer"],
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1.5px solid #DCD0D6 !important;
        border-radius: 12px !important;
        box-shadow: none !important;
        overflow: hidden !important;
    }

    /* Force light background on EVERY nested div inside selectbox & inputs */
    [data-testid="stTextInputRootElement"] *,
    [data-testid="stNumberInputContainer"] > div,
    [data-baseweb="input"],
    [data-baseweb="input"] *,
    [data-baseweb="base-input"],
    [data-baseweb="base-input"] *,
    [data-testid="stSelectbox"] [data-baseweb="select"] * {
        background-color: #FFFFFF !important;
        border-color: transparent !important;
        box-shadow: none !important;
        color: #1E161A !important;
    }

    /* Force Safari & BaseWeb light rendering on Selectbox */
    [data-testid="stSelectbox"],
    [data-testid="stSelectbox"] * {
        color-scheme: light !important;
        background-image: none !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div > div:last-child {
        background: #F6EEF2 !important;
        background-color: #F6EEF2 !important;
        border-left: 1px solid #EAE2E6 !important;
        padding: 0 0.75rem !important;
        display: flex !important;
        align-items: center !important;
    }
    [data-testid="stSelectbox"] svg {
        background: transparent !important;
        background-color: transparent !important;
        fill: #8A244E !important;
        color: #8A244E !important;
    }

    /* Dropdown popover menu list */
    [data-baseweb="popover"],
    [data-baseweb="popover"] > div,
    [data-baseweb="menu"],
    ul[role="listbox"] {
        background-color: #FFFFFF !important;
        border: 1px solid #DCD0D6 !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 25px rgba(30, 22, 26, 0.08) !important;
    }
    ul[role="listbox"] li,
    [role="option"] {
        background-color: #FFFFFF !important;
        color: #1E161A !important;
    }
    ul[role="listbox"] li:hover,
    [role="option"]:hover,
    [aria-selected="true"][role="option"] {
        background-color: #F6EEF2 !important;
        color: #8A244E !important;
        font-weight: 600 !important;
    }

    /* Input fields */
    input, input[type="text"], input[type="number"], select {
        background-color: #FFFFFF !important;
        color: #1E161A !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
    }
    input::placeholder {
        color: #96878E !important;
    }

    /* Stepper - and + buttons */
    [data-testid="stNumberInputStepDown"],
    [data-testid="stNumberInputStepUp"] {
        background-color: #F6EEF2 !important;
        color: #8A244E !important;
        border: none !important;
        border-left: 1px solid #EAE2E6 !important;
        border-radius: 0 !important;
    }
    [data-testid="stNumberInputStepDown"]:hover,
    [data-testid="stNumberInputStepUp"]:hover {
        background-color: #EDE0E6 !important;
    }
    [data-testid="stNumberInputStepDown"] svg,
    [data-testid="stNumberInputStepUp"] svg {
        background-color: transparent !important;
        fill: #8A244E !important;
        color: #8A244E !important;
    }

    /* Gradient Rebalancing Verdict Banner */
    .verdict-box {
        background: linear-gradient(135deg, #8A244E 0%, #A83565 100%);
        color: #FFFFFF !important;
        border-radius: 16px;
        padding: 1.55rem;
        margin-top: 1rem;
        box-shadow: 0 8px 22px rgba(138, 36, 78, 0.16);
    }
    .verdict-title {
        font-size: 0.74rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: rgba(255, 255, 255, 0.85) !important;
        margin-bottom: 0.45rem;
    }
    .verdict-main, .verdict-main strong, .verdict-main span {
        font-size: 1.02rem;
        font-weight: 400;
        line-height: 1.55;
        color: #FFFFFF !important;
    }
    .verdict-main strong {
        font-weight: 700 !important;
    }
    .mono-pill {
        background: rgba(255, 255, 255, 0.2);
        color: #FFFFFF !important;
        padding: 0.15rem 0.5rem;
        border-radius: 6px;
        font-size: 0.94rem;
        font-weight: 600;
    }

    /* Pill Buttons */
    .stButton > button, [data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #8A244E 0%, #A32F5F 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 999px !important;
        padding: 0.65rem 1.4rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        width: 100%;
        box-shadow: 0 4px 12px rgba(138, 36, 78, 0.18);
    }
    .stButton > button p, [data-testid="stFormSubmitButton"] > button p {
        color: #FFFFFF !important;
    }
    .stButton > button:hover {
        opacity: 0.93;
        transform: translateY(-1px);
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem;
        border-bottom: 1px solid var(--border-subtle);
        margin-bottom: 1.3rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        padding-bottom: 0.85rem !important;
    }
    .stTabs [data-baseweb="tab"] p {
        color: #75646C !important;
    }
    .stTabs [aria-selected="true"] p {
        color: #8A244E !important;
        font-weight: 700 !important;
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid #8A244E !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- STATE INITIALIZATION ---
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {
        "SWDA (MSCI World)": 4500.0,
        "CSSPX (S&P 500)": 3000.0,
        "IUIT (S&P 500 Info Tech)": 2000.0,
        "EIMI (MSCI Emerging Markets)": 500.0,
    }

if "vault_items" not in st.session_state:
    st.session_state.vault_items = [
        {
            "name": "Vintage Designer Jacket",
            "amount": 140.0,
            "category": "Fashion",
            "created_at": datetime.now() - timedelta(hours=18),
            "total_hours": COOLING_OFF_HOURS,
            "status": "active",
        }
    ]

if "saved_capital" not in st.session_state:
    st.session_state.saved_capital = 260.0

if "impulses_defeated" not in st.session_state:
    st.session_state.impulses_defeated = 3

if "purchases_confirmed" not in st.session_state:
    st.session_state.purchases_confirmed = 0

# --- HEADER ---
st.markdown(
    """
    <div class="vespera-header">
        <div class="vespera-logo">✦ vespera</div>
        <div class="vespera-badge">Behavioral Shield & Quantitative X-Ray</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Educational prototype — not financial advice. Demo data resets when the page is reloaded."
)

# --- MAIN NAVIGATION ---
tab1, tab2 = st.tabs(["01 · Behavioral Shield (FOMO Vault)", "02 · Portfolio X-Ray & Allocation"])

# ==============================================================================
# TAB 1: BEHAVIORAL SHIELD
# ==============================================================================
with tab1:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
            <div class="v-card">
                <div class="v-label">Capital Shielded from FOMO</div>
                <div class="v-metric">€ {st.session_state.saved_capital:,.2f}</div>
                <div class="v-sub">Unlocked and ready for smart allocation</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="v-card">
                <div class="v-label">Impulses Neutralized</div>
                <div class="v-metric">{st.session_state.impulses_defeated}</div>
                <div class="v-sub">Behavioral Win Rate: 85%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        projected_5y = st.session_state.saved_capital * ((1 + 0.075) ** 5)
        st.markdown(
            f"""
            <div class="v-card">
                <div class="v-label">Projected Future Value (5Y)</div>
                <div class="v-metric" style="color: #8A244E !important;">€ {projected_5y:,.2f}</div>
                <div class="v-sub">Compounded at 7.5% annualized market return</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1, 1.35], gap="large")

    with col_left:
        st.markdown("#### Lock a New Impulse")
        st.caption("Log a non-essential purchase to initiate a 72-hour cooling-off contract.")
        with st.form("fomo_form", clear_on_submit=True):
            item_name = st.text_input("Desired Item", placeholder="e.g., Limited Edition Sneakers")
            item_amount = st.number_input("Amount (€)", min_value=10.0, max_value=10000.0, value=120.0, step=10.0)
            item_cat = st.selectbox("Category", ["Fashion", "Beauty & Skincare", "Tech & Gadgets", "Lifestyle"])
            submitted = st.form_submit_button("Start Cooling-off Contract (72h)")

            if submitted and item_name.strip():
                st.session_state.vault_items.insert(
                    0,
                    {
                        "name": item_name.strip(),
                        "amount": float(item_amount),
                        "category": item_cat,
                        "created_at": datetime.now(),
                        "total_hours": COOLING_OFF_HOURS,
                        "status": "active",
                    },
                )
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Active Contracts")
        active_items = [x for x in st.session_state.vault_items if x["status"] == "active"]

        if not active_items:
            st.info("No impulse purchases pending. Your discipline is glowing.")
        else:
            for idx, item in enumerate(active_items):
                hours_left = hours_remaining(item["created_at"], item["total_hours"])
                progress_pct = int(((item["total_hours"] - hours_left) / item["total_hours"]) * 100)
                status_text = (
                    f"{hours_left:.0f}h remaining until unlock"
                    if hours_left > 0
                    else "Cooling-off complete: time to decide"
                )
                st.markdown(
                    f"""
                    <div class="v-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:600; font-size:1.05rem; color:#1E161A;">{html.escape(item['name'])}</span>
                            <span style="font-weight:600; font-size:1.05rem; color:#D9534F !important;">€ {item['amount']:.2f}</span>
                        </div>
                        <div class="v-sub">{html.escape(item['category'])} · {status_text}</div>
                        <div style="background:#F3E8ED; height:6px; width:100%; margin:0.95rem 0 0.2rem 0; border-radius:999px;">
                            <div style="background:linear-gradient(90deg, #8A244E, #C95B86); height:6px; width:{max(progress_pct, 22)}%; border-radius:999px;"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                btn_invest, btn_buy = st.columns(2)
                with btn_invest:
                    if st.button(f"Skip it & invest € {item['amount']:.0f}", key=f"win_{idx}"):
                        item["status"] = "won"
                        st.session_state.saved_capital += item["amount"]
                        st.session_state.impulses_defeated += 1
                        st.rerun()
                with btn_buy:
                    if st.button(
                        "I still want it · confirm purchase",
                        key=f"buy_{idx}",
                        disabled=hours_left > 0,
                        help="Available only after the cooling-off period ends.",
                    ):
                        item["status"] = "purchased"
                        st.session_state.purchases_confirmed += 1
                        st.rerun()

    with col_right:
        st.markdown("#### Real Opportunity Cost Analysis")
        target_amount = active_items[0]["amount"] if active_items else 120.0
        target_label = active_items[0]["name"] if active_items else "Sample Impulse (€ 120)"

        st.caption(f"5-year trajectory comparison for: {target_label} (€ {target_amount:.2f})")
        target_category = active_items[0]["category"] if active_items else "Fashion"
        df_opp = simulate_opportunity_cost(target_amount, years=5, category=target_category)
        df_sc = simulate_return_scenarios(target_amount, years=5)
        low_rate, base_rate, high_rate = (RETURN_SCENARIOS[k] * 100 for k in ("Low", "Base", "High"))

        fig_opp = go.Figure()
        fig_opp.add_trace(
            go.Scatter(
                x=df_sc["Years"],
                y=df_sc["Low"],
                mode="lines",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        fig_opp.add_trace(
            go.Scatter(
                x=df_sc["Years"],
                y=df_sc["High"],
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                fillcolor="rgba(138, 36, 78, 0.12)",
                name=f"Scenario range ({low_rate:.1f}%–{high_rate:.1f}% p.a.)",
                hoverinfo="skip",
            )
        )
        fig_opp.add_trace(
            go.Scatter(
                x=df_opp["Years"],
                y=df_opp["Invested Capital (€)"],
                mode="lines",
                name=f"Base case (+{base_rate:.1f}% p.a.)",
                line=dict(color="#8A244E", width=3.2),
            )
        )
        fig_opp.add_trace(
            go.Scatter(
                x=df_opp["Years"],
                y=df_opp["Residual Item Value (€)"],
                mode="lines",
                name="Residual Item Value (Depreciation)",
                line=dict(color="#D9534F", width=2.4, dash="dot"),
            )
        )
        fig_opp.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            margin=dict(l=25, r=25, t=40, b=25),
            height=355,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.03,
                xanchor="left",
                x=0,
                font=dict(family="Outfit, sans-serif", color="#1E161A", size=12),
            ),
            xaxis=dict(
                title=dict(text="Time Horizon (Years)", font=dict(family="Outfit, sans-serif", color="#1E161A", size=12)),
                tickfont=dict(family="Outfit, sans-serif", color="#685860", size=11),
                showgrid=False,
                linecolor="#EAE2E6",
            ),
            yaxis=dict(
                title=dict(text="Value (€)", font=dict(family="Outfit, sans-serif", color="#1E161A", size=12)),
                tickfont=dict(family="Outfit, sans-serif", color="#685860", size=11),
                gridcolor="#F7F2F4",
                linecolor="#EAE2E6",
            ),
            font=dict(family="Outfit, sans-serif", color="#1E161A", size=12),
        )
        st.plotly_chart(fig_opp, width="stretch")
        st.caption(
            "Illustrative scenarios, not forecasts. Item value uses an assumed "
            f"annual depreciation for the category “{target_category}”."
        )

        rebalance_preview = recommend_rebalance(st.session_state.portfolio, st.session_state.saved_capital)
        st.markdown(
            f"""
            <div class="verdict-box">
                <div class="verdict-title">✦ Quantitative Bridge · Recommended Action</div>
                <div class="verdict-main">
                    You have accumulated <span class="mono-pill">€ {st.session_state.saved_capital:.2f}</span> by resisting FOMO. 
                    Allocating it to <strong>{rebalance_preview['recommended_etf']}</strong> raises your Diversification Score 
                    from <span class="mono-pill">{rebalance_preview['current_score']}</span> to <span class="mono-pill">{rebalance_preview['new_score']}/100</span>.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==============================================================================
# TAB 2: PORTFOLIO X-RAY & ALLOCATION
# ==============================================================================
with tab2:
    xray = compute_portfolio_xray(st.session_state.portfolio)
    rebalance = recommend_rebalance(st.session_state.portfolio, st.session_state.saved_capital)

    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(
            f"""
            <div class="v-card">
                <div class="v-label">Diversification Score</div>
                <div class="v-metric" style="color:#8A244E !important;">{xray['score']} <span style="font-size:1.15rem; color:#685860 !important;">/ 100</span></div>
                <div class="v-sub">Computed from true underlying equity weights</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f"""
            <div class="v-card">
                <div class="v-label">Concentration Index (HHI)</div>
                <div class="v-metric">{xray['hhi']:.4f}</div>
                <div class="v-sub">Lower HHI indicates reduced idiosyncratic risk</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k3:
        top_stock = xray["single_stocks"].iloc[0]
        st.markdown(
            f"""
            <div class="v-card">
                <div class="v-label">Largest Single-Stock Exposure</div>
                <div class="v-metric" style="color:#D9534F !important;">{top_stock['Exposure (%)']:.2f}%</div>
                <div class="v-sub">Hidden overlap concentrated in <strong>{top_stock['Asset']}</strong></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    p_left, p_right = st.columns([1, 1.4], gap="large")

    with p_left:
        st.markdown("#### Declared ETF Holdings")
        st.caption("Adjust your ETF allocations to observe real-time shifts in underlying concentration.")
        st.caption(ETF_DATA_NOTE)

        updated_portfolio = {}
        for etf_name, current_val in st.session_state.portfolio.items():
            updated_portfolio[etf_name] = st.number_input(
                etf_name, min_value=0.0, max_value=1000000.0, value=float(current_val), step=250.0
            )
        st.session_state.portfolio = updated_portfolio

        if st.session_state.saved_capital > 0:
            st.markdown(
                f"""
                <div class="verdict-box">
                    <div class="verdict-title">✦ Marginal HHI Optimizer</div>
                    <div class="verdict-main">
                        Deploy your shielded <span class="mono-pill">€ {st.session_state.saved_capital:.2f}</span> into:<br>
                        <strong>{rebalance['recommended_etf']}</strong><br><br>
                        <span style="font-size:0.9rem; opacity:0.92;">
                        HHI: {rebalance['current_hhi']:.5f} → {rebalance['new_hhi']:.5f} 
                        (+{rebalance['score_delta']} pts diversification)
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Execute Rebalance with Shielded Capital"):
                target = rebalance["recommended_etf"]
                st.session_state.portfolio[target] += st.session_state.saved_capital
                st.session_state.saved_capital = 0.0
                st.rerun()

    with p_right:
        st.markdown("#### True Underlying Exposure (Top 8 Holdings)")
        st.caption("Weighted aggregation of individual equities across all held ETFs.")

        top_8 = xray["single_stocks"].head(8).iloc[::-1]

        fig_bar = go.Figure(
            go.Bar(
                x=top_8["Exposure (%)"],
                y=top_8["Asset"],
                orientation="h",
                marker=dict(
                    color=[
                        "#D9534F" if val > 7.5 else "#8A244E"
                        for val in top_8["Exposure (%)"]
                    ],
                    cornerradius=6,
                ),
                text=[f"{val:.2f}%" for val in top_8["Exposure (%)"]],
                textposition="outside",
                textfont=dict(family="Outfit, sans-serif", size=12, color="#1E161A"),
            )
        )
        fig_bar.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            margin=dict(l=15, r=55, t=20, b=25),
            height=410,
            xaxis=dict(
                title=dict(text="True Weight in Total Portfolio (%)", font=dict(family="Outfit, sans-serif", color="#1E161A", size=12)),
                tickfont=dict(family="Outfit, sans-serif", color="#685860", size=11),
                showgrid=True,
                gridcolor="#F7F2F4",
                range=[0, max(top_8["Exposure (%)"]) * 1.24],
            ),
            yaxis=dict(
                tickfont=dict(family="Outfit, sans-serif", color="#1E161A", size=12),
                showgrid=False,
            ),
            font=dict(family="Outfit, sans-serif", color="#1E161A", size=12),
        )
        st.plotly_chart(fig_bar, width="stretch")

st.markdown("<br>", unsafe_allow_html=True)
st.caption(
    "Vespera is an educational prototype. Nothing shown here is investment advice or a recommendation "
    "to buy or sell any financial product."
)
