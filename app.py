import streamlit as st
import plotly.graph_objects as go
from engine import (
    ETF_HOLDINGS,
    compute_portfolio_xray,
    recommend_rebalance,
    simulate_opportunity_cost,
)

st.set_page_config(
    page_title="Vespera — Behavioral & Quantitative Wealth",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --bg-primary: #F9F9F8;
        --surface: #FFFFFF;
        --border-subtle: #E5E5E0;
        --text-primary: #111111;
        --text-secondary: #6E6E73;
        --accent-forest: #0F3D3E;
        --accent-terracotta: #B85042;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }

    .stApp {
        background-color: var(--bg-primary);
    }

    /* Hide default Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Brand Header */
    .vespera-header {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        padding: 1.2rem 0 1.8rem 0;
        border-bottom: 1px solid var(--border-subtle);
        margin-bottom: 2rem;
    }
    .vespera-logo {
        font-size: 1.65rem;
        font-weight: 600;
        letter-spacing: -0.03em;
        color: var(--text-primary);
    }
    .vespera-tagline {
        font-size: 0.85rem;
        color: var(--text-secondary);
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }

    /* Institutional Cards */
    .v-card {
        background-color: var(--surface);
        border: 1px solid var(--border-subtle);
        border-radius: 6px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
    }
    .v-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--text-secondary);
        margin-bottom: 0.4rem;
        font-weight: 500;
    }
    .v-metric {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.1rem;
        font-weight: 500;
        color: var(--text-primary);
        letter-spacing: -0.02em;
    }
    .v-sub {
        font-size: 0.82rem;
        color: var(--text-secondary);
        margin-top: 0.3rem;
    }

    /* Rebalancing Verdict Banner */
    .verdict-box {
        background-color: var(--accent-forest);
        color: #FFFFFF;
        border-radius: 6px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    .verdict-title {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        opacity: 0.8;
        margin-bottom: 0.4rem;
    }
    .verdict-main {
        font-size: 1.15rem;
        font-weight: 500;
        line-height: 1.45;
    }
    .mono-pill {
        font-family: 'JetBrains Mono', monospace;
        background: rgba(255,255,255,0.14);
        padding: 0.15rem 0.45rem;
        border-radius: 4px;
        font-size: 0.92rem;
    }

    /* Minimal Buttons */
    .stButton > button {
        background-color: var(--accent-forest) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 0.55rem 1.2rem !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.01em !important;
        transition: opacity 0.2s ease;
    }
    .stButton > button:hover {
        opacity: 0.9;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 1px solid var(--border-subtle);
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.92rem;
        font-weight: 500;
        color: var(--text-secondary);
        padding-bottom: 0.8rem;
    }
    .stTabs [aria-selected="true"] {
        color: var(--text-primary) !important;
        border-bottom: 2px solid var(--accent-forest) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


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
            "category": "Fashion / FOMO",
            "hours_left": 54,
            "total_hours": 72,
            "status": "active",
        }
    ]

if "saved_capital" not in st.session_state:
    st.session_state.saved_capital = 260.0

if "impulses_defeated" not in st.session_state:
    st.session_state.impulses_defeated = 3


st.markdown(
    """
    <div class="vespera-header">
        <div class="vespera-logo">◈ Vespera</div>
        <div class="vespera-tagline">Behavioral Shield & Quantitative X-Ray</div>
    </div>
    """,
    unsafe_allow_html=True,
)


tab1, tab2 = st.tabs(["01 · Behavioral Shield (FOMO Vault)", "02 · Portfolio X-Ray & Allocation"])

with tab1:
    # KPI Row
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
            <div class="v-card">
                <div class="v-label">Capital Shielded from FOMO</div>
                <div class="v-metric">€ {st.session_state.saved_capital:,.2f}</div>
                <div class="v-sub">Unlocked and ready for quantitative allocation</div>
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
                <div class="v-metric" style="color: #0F3D3E;">€ {projected_5y:,.2f}</div>
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
            item_cat = st.selectbox("Category", ["Fashion / FOMO", "Tech & Gadgets", "Lifestyle", "Other"])
            submitted = st.form_submit_button("Start Cooling-off Contract (72h)")

            if submitted and item_name.strip():
                st.session_state.vault_items.insert(
                    0,
                    {
                        "name": item_name.strip(),
                        "amount": float(item_amount),
                        "category": item_cat,
                        "hours_left": 72,
                        "total_hours": 72,
                        "status": "active",
                    },
                )
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Active Contracts")
        active_items = [x for x in st.session_state.vault_items if x["status"] == "active"]

        if not active_items:
            st.info("No impulse purchases pending. Your discipline is intact.")
        else:
            for idx, item in enumerate(active_items):
                progress_pct = int(((item["total_hours"] - item["hours_left"]) / item["total_hours"]) * 100)
                st.markdown(
                    f"""
                    <div class="v-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:500; font-size:1rem;">{item['name']}</span>
                            <span style="font-family:'JetBrains Mono', monospace; font-weight:600; color:#B85042;">€ {item['amount']:.2f}</span>
                        </div>
                        <div class="v-sub">{item['category']} · {item['hours_left']}h remaining until unlock</div>
                        <div style="background:#E5E5E0; height:3px; width:100%; margin:0.9rem 0; border-radius:2px;">
                            <div style="background:#0F3D3E; height:3px; width:{max(progress_pct, 15)}%;"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(f"Forfeit Purchase & Transfer € {item['amount']:.0f} to Portfolio", key=f"win_{idx}"):
                    item["status"] = "won"
                    st.session_state.saved_capital += item["amount"]
                    st.session_state.impulses_defeated += 1
                    st.rerun()

    with col_right:
        st.markdown("#### Real Opportunity Cost Analysis")
        target_amount = active_items[0]["amount"] if active_items else 120.0
        target_label = active_items[0]["name"] if active_items else "Sample Impulse (€ 120)"

        st.caption(f"5-year trajectory comparison for: **{target_label} (€ {target_amount:.2f})**")
        df_opp = simulate_opportunity_cost(target_amount, years=5)

        fig_opp = go.Figure()
        fig_opp.add_trace(
            go.Scatter(
                x=df_opp["Years"],
                y=df_opp["Invested Capital (€)"],
                mode="lines",
                name="Invested Capital (+7.5% p.a.)",
                line=dict(color="#0F3D3E", width=2.5),
            )
        )
        fig_opp.add_trace(
            go.Scatter(
                x=df_opp["Years"],
                y=df_opp["Residual Item Value (€)"],
                mode="lines",
                name="Residual Item Value (Depreciation)",
                line=dict(color="#B85042", width=2, dash="dot"),
            )
        )
        fig_opp.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            margin=dict(l=20, r=20, t=25, b=20),
            height=340,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            xaxis=dict(title="Time Horizon (Years)", showgrid=False, linecolor="#E5E5E0"),
            yaxis=dict(title="Value (€)", gridcolor="#F0F0EC", linecolor="#E5E5E0"),
            font=dict(family="Inter, sans-serif", color="#111111", size=12),
        )
        st.plotly_chart(fig_opp, use_container_width=True)

        # Direct bridge to Tab 2
        rebalance_preview = recommend_rebalance(st.session_state.portfolio, st.session_state.saved_capital)
        st.markdown(
            f"""
            <div class="verdict-box">
                <div class="verdict-title">Quantitative Bridge · Recommended Action</div>
                <div class="verdict-main">
                    You have accumulated <span class="mono-pill">€ {st.session_state.saved_capital:.2f}</span> by resisting FOMO. 
                    Allocating it to <strong>{rebalance_preview['recommended_etf']}</strong> raises your Diversification Score 
                    from <span class="mono-pill">{rebalance_preview['current_score']}</span> to <span class="mono-pill">{rebalance_preview['new_score']}/100</span>.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with tab2:
    xray = compute_portfolio_xray(st.session_state.portfolio)
    rebalance = recommend_rebalance(st.session_state.portfolio, st.session_state.saved_capital)

    # KPI Row
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(
            f"""
            <div class="v-card">
                <div class="v-label">Diversification Score</div>
                <div class="v-metric" style="color:#0F3D3E;">{xray['score']} <span style="font-size:1.1rem; color:#6E6E73;">/ 100</span></div>
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
                <div class="v-metric" style="color:#B85042;">{top_stock['Exposure (%)']:.2f}%</div>
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
                    <div class="verdict-title">Marginal HHI Optimizer</div>
                    <div class="verdict-main">
                        Deploy your shielded <span class="mono-pill">€ {st.session_state.saved_capital:.2f}</span> into:<br>
                        <strong>{rebalance['recommended_etf']}</strong><br><br>
                        <span style="font-size:0.88rem; opacity:0.9;">
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
                        "#B85042" if val > 7.5 else "#0F3D3E"
                        for val in top_8["Exposure (%)"]
                    ]
                ),
                text=[f"{val:.2f}%" for val in top_8["Exposure (%)"]],
                textposition="outside",
                textfont=dict(family="JetBrains Mono, monospace", size=12, color="#111111"),
            )
        )
        fig_bar.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            margin=dict(l=10, r=45, t=15, b=20),
            height=400,
            xaxis=dict(
                title="True Weight in Total Portfolio (%)",
                showgrid=True,
                gridcolor="#F0F0EC",
                range=[0, max(top_8["Exposure (%)"]) * 1.22],
            ),
            yaxis=dict(showgrid=False),
            font=dict(family="Inter, sans-serif", color="#111111", size=12),
        )
        st.plotly_chart(fig_bar, use_container_width=True)
