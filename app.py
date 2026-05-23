"""
Case 3 — Food Delivery Demand Pulse
Streamlit dashboard for the Ops Head
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Food Delivery — Demand Pulse",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background:#1e1e2e;
        border-radius:12px;
        padding:18px 22px;
        border-left:4px solid #FF6B35;
        margin-bottom:8px;
    }

    .metric-label {
        color:#90A4AE;
        font-size:13px;
        margin-bottom:4px;
    }

    .metric-value {
        color:#ffffff;
        font-size:28px;
        font-weight:700;
    }

    .metric-delta {
        font-size:12px;
        margin-top:2px;
    }

    .section-header {
        font-size:18px;
        font-weight:700;
        color:#FF6B35;
        margin:24px 0 8px 0;
        border-bottom:1px solid #2a2a3e;
        padding-bottom:6px;
    }

    [data-testid="stSidebar"] {
        background-color:#12121f;
    }
</style>
""", unsafe_allow_html=True)

# ── Theme Colors ──────────────────────────────────────────────────────────────
PALETTE = {
    "primary": "#FF6B35",
    "secondary": "#2D4A6A",
    "accent": "#FFC947",
    "neutral": "#90A4AE",
}

CITY_COLORS = {
    "Bangalore": "#FF6B35",
    "Mumbai": "#FFC947",
    "Delhi": "#4FC3F7",
    "Hyderabad": "#81C784",
    "Chennai": "#CE93D8",
    "Pune": "#F48FB1",
    "Kolkata": "#90A4AE",
}

# ── Data Loader ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("case3_food_delivery_orders.csv")

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["dow"] = df["timestamp"].dt.dayofweek
    df["day_name"] = df["timestamp"].dt.day_name()
    df["is_weekend"] = df["dow"] >= 5
    df["date"] = df["timestamp"].dt.date

    df["period"] = df["hour"].apply(
        lambda h:
        "Dinner Peak (19-21)" if h in [19,20,21]
        else "Lunch Peak (12-13)" if h in [12,13]
        else "Off-Peak"
    )

    return df

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:

    st.markdown("## 🛵 Demand Pulse")
    st.markdown("*Ops Head Dashboard — Case 3*")

    st.divider()

    st.markdown("### Filters")

    selected_cities = st.multiselect(
        "Cities",
        sorted(df["city"].unique()),
        default=sorted(df["city"].unique())
    )

    selected_cuisines = st.multiselect(
        "Cuisines",
        sorted(df["cuisine"].unique()),
        default=sorted(df["cuisine"].unique())
    )

    hour_range = st.slider(
        "Hour of Day",
        0,
        23,
        (0,23)
    )

    date_min = df["date"].min()
    date_max = df["date"].max()

    date_range = st.date_input(
        "Date Range",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max
    )

    st.divider()

    surge_cost = st.number_input(
        "Surge incentive per order (Rs.)",
        min_value=10,
        max_value=100,
        value=25,
        step=5
    )

# ── Filtering ─────────────────────────────────────────────────────────────────
if not selected_cities:
    st.warning("Please select at least one city.")
    st.stop()

d_start, d_end = (
    date_range[0],
    date_range[1]
)

mask = (
    df["city"].isin(selected_cities)
    &
    df["cuisine"].isin(selected_cuisines)
    &
    df["hour"].between(hour_range[0], hour_range[1])
    &
    (df["date"] >= d_start)
    &
    (df["date"] <= d_end)
)

dff = df[mask].copy()

if dff.empty:
    st.error("No data available for selected filters.")
    st.stop()

n_days = max(
    (pd.Timestamp(d_end) - pd.Timestamp(d_start)).days,
    1
)

# ── Safe percentage helper ───────────────────────────────────────────────────
def pct(num, den):
    return f"{(num / den) * 100:.1f}%" if den > 0 else "N/A"

# ── KPI Function ──────────────────────────────────────────────────────────────
def kpi(col, label, value, delta=None, good=True):

    color = "#4CAF50" if good else "#FF5252"

    delta_html = (
        f'<div class="metric-delta" style="color:{color}">{delta}</div>'
        if delta else ""
    )

    col.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🛵 Food Delivery Demand Pulse")

st.markdown(
    f"""
    **{len(dff):,} orders**
    · {len(selected_cities)} cities
    · {d_start} → {d_end}
    """
)

st.divider()

# ── KPIs ──────────────────────────────────────────────────────────────────────
off_peak_hours = list(range(0,10)) + [22,23]

wasted_surge = dff[
    dff["hour"].isin(off_peak_hours)
]["surge_applied"].sum()

monthly_saving = wasted_surge * surge_cost * (30 / n_days)

k1,k2,k3,k4,k5 = st.columns(5)

kpi(k1, "Total Orders", f"{len(dff):,}")

kpi(
    k2,
    "Surge Rate",
    f"{dff['surge_applied'].mean()*100:.1f}%"
)

kpi(
    k3,
    "Avg Order Value",
    f"Rs.{dff['order_value'].mean():.0f}"
)

kpi(
    k4,
    "Avg Delivery Time",
    f"{dff['delivery_time_min'].mean():.1f} min"
)

kpi(
    k5,
    "Potential Monthly Saving",
    f"Rs.{monthly_saving:,.0f}"
)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "⏰ Hourly Demand",
    "🏙️ City Analysis",
    "💰 Surge Waste"
])

# ── TAB 1 ─────────────────────────────────────────────────────────────────────
with tab1:

    st.markdown(
        '<div class="section-header">Orders & Surge by Hour</div>',
        unsafe_allow_html=True
    )

    hourly = (
        dff.groupby("hour")
        .agg(
            orders=("order_id", "count"),
            surge_rate=("surge_applied", "mean")
        )
        .reset_index()
    )

    hourly["surge_pct"] = hourly["surge_rate"] * 100

    # ── Orders + Surge Dual Axis ────────────────────────────────────────────
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=hourly["hour"],
            y=hourly["orders"],
            name="Orders",
            marker_color=PALETTE["primary"]
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=hourly["hour"],
            y=hourly["surge_pct"],
            mode="lines+markers",
            name="Surge Rate (%)",
            line=dict(color=PALETTE["accent"], width=3)
        ),
        secondary_y=True
    )

    fig.update_layout(
        title="Orders vs Surge Rate by Hour",
        plot_bgcolor="#12121f",
        paper_bgcolor="#12121f",
        font_color="#e0e0e0",
        height=450,
        xaxis=dict(
            tickmode="linear",
            dtick=1
        )
    )

    fig.update_yaxes(title_text="Orders", secondary_y=False)
    fig.update_yaxes(title_text="Surge Rate (%)", secondary_y=True)

    st.plotly_chart(fig, use_container_width=True)

    # ── Surge Rate vs Hour ──────────────────────────────────────────────────
    st.markdown("### 📈 Surge Rate vs Hour")

    surge_hourly = (
        dff.groupby("hour")
        .agg(
            total_orders=("order_id", "count"),
            surge_orders=("surge_applied", "sum")
        )
        .reset_index()
    )

    surge_hourly["surge_pct"] = np.where(
        surge_hourly["total_orders"] > 0,
        (
            surge_hourly["surge_orders"]
            /
            surge_hourly["total_orders"]
        ) * 100,
        0
    )

    fig2 = px.line(
        surge_hourly,
        x="hour",
        y="surge_pct",
        markers=True,
        title="Surge Rate by Hour",
        labels={
            "hour":"Hour of Day",
            "surge_pct":"Surge Rate (%)"
        }
    )

    fig2.add_vrect(
        x0=11.5,
        x1=14,
        fillcolor=PALETTE["accent"],
        opacity=0.08,
        line_width=0
    )

    fig2.add_vrect(
        x0=18.5,
        x1=22,
        fillcolor=PALETTE["primary"],
        opacity=0.08,
        line_width=0
    )

    fig2.update_layout(
        plot_bgcolor="#12121f",
        paper_bgcolor="#12121f",
        font_color="#e0e0e0",
        height=380,
        xaxis=dict(
            tickmode="linear",
            dtick=1
        )
    )

    st.plotly_chart(fig2, use_container_width=True)

    # ── Surge Breakdown Table ───────────────────────────────────────────────
    st.markdown("### 📊 Surge Breakdown by Hour Block")

    hgroups = {
        "Dinner (19-21)": [19,20,21],
        "Lunch (12-13)": [12,13],
        "Transition (10-11,14-18)": [10,11,14,15,16,17,18],
        "Night (0-9,22-23)": list(range(0,10)) + [22,23]
    }

    rows = []

    for label, hours in hgroups.items():

        sub = dff[dff["hour"].isin(hours)]

        tot = len(sub)

        sur = int(sub["surge_applied"].sum())

        rows.append({
            "Hour Block": label,
            "Orders": tot,
            "Surge Orders": sur,
            "Surge %": pct(sur, tot)
        })

    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True
    )

# ── TAB 2 ─────────────────────────────────────────────────────────────────────
with tab2:

    st.markdown(
        '<div class="section-header">City Demand Analysis</div>',
        unsafe_allow_html=True
    )

    city_hour = (
        dff.groupby(["city","hour"])["order_id"]
        .count()
        .reset_index(name="orders")
    )

    fig3 = px.line(
        city_hour,
        x="hour",
        y="orders",
        color="city",
        markers=True,
        title="Orders by Hour for All Cities"
    )

    fig3.update_layout(
        plot_bgcolor="#12121f",
        paper_bgcolor="#12121f",
        font_color="#e0e0e0",
        height=450,
        xaxis=dict(
            tickmode="linear",
            dtick=1
        )
    )

    st.plotly_chart(fig3, use_container_width=True)

    # ── Surge Rate by City ──────────────────────────────────────────────────
    surge_city = (
        dff.groupby(["city","hour"])
        .agg(
            total_orders=("order_id", "count"),
            surge_orders=("surge_applied", "sum")
        )
        .reset_index()
    )

    surge_city["surge_pct"] = np.where(
        surge_city["total_orders"] > 0,
        (
            surge_city["surge_orders"]
            /
            surge_city["total_orders"]
        ) * 100,
        0
    )

    fig4 = px.line(
        surge_city,
        x="hour",
        y="surge_pct",
        color="city",
        markers=True,
        title="Surge Rate by Hour for All Cities"
    )

    fig4.update_layout(
        plot_bgcolor="#12121f",
        paper_bgcolor="#12121f",
        font_color="#e0e0e0",
        height=450,
        xaxis=dict(
            tickmode="linear",
            dtick=1
        )
    )

    st.plotly_chart(fig4, use_container_width=True)

# ── TAB 3 ─────────────────────────────────────────────────────────────────────
with tab3:

    st.markdown(
        '<div class="section-header">Surge Waste Calculator</div>',
        unsafe_allow_html=True
    )

    hgroups = {
        "Dinner (19-21) HIGH Demand": [19,20,21],
        "Lunch (12-13) Medium Demand": [12,13],
        "Transition (10-11,14-18)": [10,11,14,15,16,17,18],
        "Night (0-9,22-23) WASTED": list(range(0,10)) + [22,23]
    }

    rows = []

    for label, hours in hgroups.items():

        sub = dff[dff["hour"].isin(hours)]

        tot = len(sub)

        sur = int(sub["surge_applied"].sum())

        rows.append({
            "Hour Block": label,
            "Total Orders": f"{tot:,}",
            "Surge Orders": f"{sur:,}",
            "Surge %": pct(sur, tot),
            "Monthly Cost Rs.": f"{sur * surge_cost * (30/n_days):,.0f}"
        })

    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True
    )

    # ── Waste Chart ─────────────────────────────────────────────────────────
    surge_hourly2 = (
        dff.groupby("hour")
        .agg(
            surge_orders=("surge_applied","sum")
        )
        .reset_index()
    )

    surge_hourly2["is_waste"] = surge_hourly2["hour"].isin(
        list(range(0,10)) + [22,23]
    )

    fig5 = px.bar(
        surge_hourly2,
        x="hour",
        y="surge_orders",
        color="is_waste",
        color_discrete_map={
            True:"#FF5252",
            False:PALETTE["neutral"]
        },
        title="Surge Orders by Hour — Off-Peak Waste Highlighted"
    )

    fig5.update_layout(
        plot_bgcolor="#12121f",
        paper_bgcolor="#12121f",
        font_color="#e0e0e0",
        height=420,
        xaxis=dict(
            tickmode="linear",
            dtick=1
        )
    )

    st.plotly_chart(fig5, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()

st.markdown(
    """
    <div style='text-align:center;color:#555;font-size:12px'>
    Case 3 — Food Delivery Demand Pulse · Streamlit Dashboard
    </div>
    """,
    unsafe_allow_html=True
)
