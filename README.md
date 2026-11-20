# Vespera — Behavioral Shield & Quantitative Portfolio X-Ray

**Vespera** is a closed-loop wealth-tech prototype that bridges **Behavioral Finance** (mitigating FOMO-driven impulse spending) and **Quantitative Portfolio Analysis** (uncovering hidden ETF overlap and optimizing asset allocation).

---

### Core Architecture

The system operates as a two-stage decision engine:

1. **Behavioral Shield (FOMO Vault):**
   * Intercepts non-essential impulse purchases through **72-hour Cooling-off Contracts**.
   * Models the real **Opportunity Cost** by comparing the asset's expected depreciation curve against compound market returns ($r = 7.5\%$).
   * Converts resisted impulses into unlocked capital ready for deployment.

2. **Quantitative X-Ray & Marginal Rebalancer:**
   * Computes true underlying equity exposure across multiple UCITS ETFs:
     $$E_j = \sum_{i=1}^{N} w_i \cdot p_{i,j}$$
     where $w_i$ is the portfolio weight of ETF $i$ and $p_{i,j}$ is the weight of underlying asset $j$ within ETF $i$.
   * Quantifies hidden concentration risk via the **Herfindahl-Hirschman Index (HHI)**:
     $$\text{HHI} = \sum_{j=1}^{M} E_j^2$$
   * Simulates marginal capital allocation to recommend the exact ETF that **minimizes post-trade HHI** and maximizes the portfolio's **Diversification Score**.

---

### Tech Stack

* **Quantitative Engine:** Python (`NumPy`, `Pandas`)
* **Visualization & UI:** `Streamlit`, `Plotly`, custom CSS (*Minimal Institutional* design system)

---

### Quickstart

```bash
git clone [https://github.com/indacoelisaagata/vespera.git](https://github.com/indacoelisaagata/vespera.git)
cd vespera
pip install -r requirements.txt
streamlit run app.py
