---
title: Case3 Demand Pulse
emoji: ??
colorFrom: orange
colorTo: red
sdk: streamlit
sdk_version: "1.36.0"
app_file: app.py
pinned: false
---
# Case 3 — Food Delivery Demand Pulse 🛵

> **Live demo:** https://huggingface.co/spaces/YOUR_HF_USERNAME/case3-demand-pulse

Interactive dashboard for the Ops Head to explore food delivery demand patterns across 7 Indian cities and make data-backed surge pricing decisions.

---

## What This Does

The Ops Head suspected "peak demand" is more nuanced than the current surge rules. This dashboard lets her explore:

- **When** demand really spikes (two peaks: lunch 12–13, dinner 19–21)
- **Where** cities differ in demand skew (Chennai most dinner-heavy at 1.65x, Kolkata most lunch-balanced at 1.46x)
- **How much** the current surge policy is wasting (~₹5–7K/month on off-peak hours with no delivery pressure)
- **What** each city's cuisine identity looks like (Kolkata = Desserts, Bangalore = Biryani)

All filters are interactive — city, cuisine, hour range, date range, and surge cost per order.

---

## Run Locally

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/case3-demand-pulse.git
cd case3-demand-pulse

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Place case3_food_delivery_orders.csv in this folder, then:
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## Project Structure

```
case3-demand-pulse/
├── app.py                          # Streamlit dashboard (main file)
├── food_delivery_demand_pulse.ipynb # Full analysis notebook
├── case3_food_delivery_orders.csv   # Dataset (50K orders, 90 days)
├── requirements.txt
└── README.md
```

---

## Key Findings

| Finding | Impact |
|---------|--------|
| Two true peaks: lunch 12–13, dinner 19–21 | Surge must be time-windowed, not always-on |
| Off-peak surge (0–9, 22–23) is ~5% with zero delivery pressure | ₹5–7K/month wasted |
| Weekend surge rate 57% higher than weekdays | Pre-schedule Fri–Sun surge instead of reactive |
| All cities follow same hourly pattern, but dinner/lunch skew varies | City-specific lunch vs dinner policy needed |

---

## Screenshot

*(Add a screenshot here after deploying)*

---

## License

MIT

