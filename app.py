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

st.markdown("""
<style>
    .metric-card {
        background:#1e1e2e; border-radius:12px;
        padding:18px 22px; border-left:4px solid #FF6B35;
        margin-bottom:8px;
    }
    .metric-label { color:#90A4AE; font-size:13px; margin-bottom:4px; }
    .metric-value { color:#ffffff; font-size:28px; font-weight:700; }
    .metric-delta { font-size:12px; margin-top:2px; }
    .section-header {
        font-size:18px; font-weight:700; color:#FF6B35;
        margin:24px 0 8px 0;
        border-bottom:1px solid #2a2a3e; padding-bottom:6px;
    }
    [data-testid="stSidebar"] { background-color:#12121f; }
</style>
""", unsafe_allow_html=True)

PALETTE = {
    "primary":   "#FF6B35",
    "secondary": "#2D4A6A",
    "accent":    "#FFC947",
    "neutral":   "#90A4AE",
}
CITY_COLORS = {
    "Bangalore":"#FF6B35","Mumbai":"#FFC947","Delhi":"#4FC3F7",
    "Hyderabad":"#81C784","Chennai":"#CE93D8","Pune":"#F48FB1","Kolkata":"#90A4AE",
}

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("case3_food_delivery_orders.csv")
    df["timestamp"]  = pd.to_datetime(df["timestamp"])
    df["hour"]       = df["timestamp"].dt.hour
    df["dow"]        = df["timestamp"].dt.dayofweek
    df["day_name"]   = df["timestamp"].dt.day_name()
    df["is_weekend"] = df["dow"] >= 5
    df["date"]       = df["timestamp"].dt.date
    df["week"]       = df["timestamp"].dt.isocalendar().week.astype(int)
    df["period"]     = df["hour"].apply(lambda h:
        "Dinner Peak (19-21)" if h in [19,20,21] else
        "Lunch Peak (12-13)"  if h in [12,13]    else "Off-Peak")
    return df

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛵 Demand Pulse")
    st.markdown("*Ops Head Dashboard — Case 3*")
    st.divider()
    st.markdown("### Filters")

    all_cities   = sorted(df["city"].unique())
    all_cuisines = sorted(df["cuisine"].unique())

    selected_cities = st.multiselect(
        "Cities", all_cities, default=all_cities)
    selected_cuisines = st.multiselect(
        "Cuisines", all_cuisines, default=all_cuisines)
    hour_range = st.slider(
        "Hour of Day", 0, 23, (0, 23))
    date_min, date_max = df["date"].min(), df["date"].max()
    date_range = st.date_input(
        "Date Range", value=(date_min, date_max),
        min_value=date_min, max_value=date_max)

    st.divider()
    surge_cost = st.number_input(
        "Surge incentive per order (Rs.)", 10, 100, 25, 5)

    st.divider()
    st.markdown("**Cohort thresholds**")
    tier1_min = st.number_input("Tier 1 min orders", value=9000, step=500)
    tier2_min = st.number_input("Tier 2 min orders", value=5500, step=500)

# ── Filter ────────────────────────────────────────────────────────────────────
if not selected_cities:
    st.warning("Please select at least one city.")
    st.stop()

d_start, d_end = (date_range[0], date_range[1]) if len(date_range)==2 else (date_min, date_max)

mask = (
    df["city"].isin(selected_cities) &
    df["cuisine"].isin(selected_cuisines) &
    df["hour"].between(hour_range[0], hour_range[1]) &
    (df["date"] >= d_start) &
    (df["date"] <= d_end)
)
dff = df[mask].copy()

if dff.empty:
    st.error("No data for selected filters.")
    st.stop()

n_days = max((pd.Timestamp(d_end) - pd.Timestamp(d_start)).days, 1)

# ── Header + KPIs ─────────────────────────────────────────────────────────────
st.markdown("# 🛵 Food Delivery Demand Pulse")
st.markdown(
    f"**{len(dff):,} orders** · "
    f"{len(selected_cities)} cit{'y' if len(selected_cities)==1 else 'ies'} · "
    f"{d_start} → {d_end}"
)
st.divider()

off_peak_hours = list(range(0,10)) + [22,23]
wasted_surge = dff[dff["hour"].isin(off_peak_hours)]["surge_applied"].sum()
monthly_saving = wasted_surge * surge_cost * (30 / n_days)

def kpi(col, label, value, delta=None, good=True):
    color = "#4CAF50" if good else "#FF5252"
    delta_html = f'<div class="metric-delta" style="color:{color}">{delta}</div>' if delta else ""
    col.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>{delta_html}</div>',
        unsafe_allow_html=True)

k1,k2,k3,k4,k5 = st.columns(5)
kpi(k1, "Total Orders",           f"{len(dff):,}")
kpi(k2, "Surge Rate",             f"{dff['surge_applied'].mean()*100:.1f}%",
    "57% higher on weekends", False)
kpi(k3, "Avg Order Value",        f"Rs.{dff['order_value'].mean():.0f}")
kpi(k4, "Avg Delivery Time",      f"{dff['delivery_time_min'].mean():.1f} min")
kpi(k5, "Est. Monthly Saving",    f"Rs.{monthly_saving:,.0f}",
    "if off-peak surge removed", True)
st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1,tab2,tab3,tab4,tab5 = st.tabs([
    "⏰ Hourly Demand",
    "📅 Day of Week",
    "🏙️ City Cohorts",
    "🍛 Cuisine Mix",
    "💰 Surge Waste",
])

# ── TAB 1: Hourly ─────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-header">Orders & Surge Rate by Hour</div>',
                unsafe_allow_html=True)

    hourly = (
        dff.groupby("hour")
           .agg(orders=("order_id","count"),
                surge_rate=("surge_applied","mean"),
                avg_delivery=("delivery_time_min","mean"))
           .reset_index()
    )
    hourly["surge_pct"] = hourly["surge_rate"] * 100
    hourly["bar_color"] = hourly["hour"].apply(
        lambda h: PALETTE["primary"] if h in [12,13,19,20,21] else PALETTE["neutral"])

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=hourly["hour"], y=hourly["orders"],
        marker_color=hourly["bar_color"], marker_opacity=0.85, name="Orders",
        hovertemplate="Hour %{x}:00<br>Orders: %{y:,}<extra></extra>"),
        secondary_y=False)
    fig.add_trace(go.Scatter(
        x=hourly["hour"], y=hourly["surge_pct"],
        mode="lines+markers", line=dict(color=PALETTE["accent"], width=2.5),
        marker=dict(size=6), name="Surge Rate (%)",
        hovertemplate="Hour %{x}:00<br>Surge: %{y:.1f}%<extra></extra>"),
        secondary_y=True)
    fig.update_layout(
        title="Order Volume vs Surge Application Rate by Hour",
        xaxis=dict(title="Hour of Day", tickmode="linear", dtick=1),
        yaxis=dict(title="Total Orders", gridcolor="#2a2a3e"),
        yaxis2=dict(title="Surge Rate (%)", gridcolor="#2a2a3e"),
        plot_bgcolor="#12121f", paper_bgcolor="#12121f",
        font_color="#e0e0e0", legend=dict(bgcolor="#1e1e2e"), height=420)
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Peak vs Off-Peak Delivery Time**")
        period_del = (
            dff.groupby("period")["delivery_time_min"].mean()
               .reindex(["Off-Peak","Lunch Peak (12-13)","Dinner Peak (19-21)"])
               .reset_index()
        )
        period_del.columns = ["Period","Avg Delivery (min)"]
        fig2 = px.bar(period_del, x="Period", y="Avg Delivery (min)",
                      color="Period",
                      color_discrete_map={
                          "Off-Peak": PALETTE["neutral"],
                          "Lunch Peak (12-13)": PALETTE["accent"],
                          "Dinner Peak (19-21)": PALETTE["primary"]},
                      text_auto=".1f")
        fig2.update_layout(
            plot_bgcolor="#12121f", paper_bgcolor="#12121f",
            font_color="#e0e0e0", showlegend=False, height=320,
            yaxis=dict(range=[37,46], gridcolor="#2a2a3e"))
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        st.markdown("**Surge Breakdown by Hour Block**")
        hgroups = {
            "Dinner (19-21)":            [19,20,21],
            "Lunch (12-13)":             [12,13],
            "Transition (10-11,14-18)":  [10,11,14,15,16,17,18],
            "Night (0-9, 22-23)":        list(range(0,10))+[22,23],
        }
        rows = []
        for label, hours in hgroups.items():
            sub = dff[dff["hour"].isin(hours)]
            tot = len(sub); sur = sub["surge_applied"].sum()
            rows.append({"Hour Block":label, "Orders":tot,
                         "Surge Ordr":int(sur), "Surge%":f"{sur/tot*100:.1f}%"})
        st.dataframe(pd.DataFrame(rows), hide_index=True,
                     use_container_width=True, height=220)

        top5 = hourly.nlargest(5,"orders")[["hour","orders","surge_pct"]]
        top5.columns = ["Hour","Orders","Surge %"]
        top5["Surge %"] = top5["Surge %"].apply(lambda x: f"{x:.1f}%")
        st.markdown("**Top 5 Demand Hours**")
        st.dataframe(top5, hide_index=True, use_container_width=True)

# ── TAB 2: Day of Week ────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-header">Day-of-Week Demand & Surge</div>',
                unsafe_allow_html=True)
    dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    dow = (
        dff.groupby("day_name")
           .agg(orders=("order_id","count"), surge_rate=("surge_applied","mean"))
           .reindex(dow_order).reset_index()
    )
    dow["surge_pct"] = dow["surge_rate"] * 100
    dow["is_weekend"] = dow["day_name"].isin(["Saturday","Sunday"])

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(dow, x="day_name", y="orders", color="is_weekend",
                     color_discrete_map={True:PALETTE["primary"], False:PALETTE["neutral"]},
                     labels={"day_name":"","orders":"Orders","is_weekend":"Weekend"},
                     title="Orders by Day of Week", text_auto=True)
        fig.update_layout(plot_bgcolor="#12121f", paper_bgcolor="#12121f",
                          font_color="#e0e0e0", showlegend=False, height=360)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        wkday_avg = dff[~dff["is_weekend"]]["surge_applied"].mean() * 100
        wkend_avg = dff[dff["is_weekend"]]["surge_applied"].mean()  * 100
        fig = px.bar(dow, x="day_name", y="surge_pct", color="is_weekend",
                     color_discrete_map={True:PALETTE["primary"], False:PALETTE["neutral"]},
                     labels={"day_name":"","surge_pct":"Surge Rate (%)","is_weekend":"Weekend"},
                     title=f"Surge Rate (Weekday: {wkday_avg:.1f}%  Weekend: {wkend_avg:.1f}%)",
                     text_auto=".1f")
        fig.add_hline(y=wkday_avg, line_dash="dash", line_color=PALETTE["neutral"],
                      annotation_text=f"Weekday {wkday_avg:.1f}%")
        fig.add_hline(y=wkend_avg, line_dash="dash", line_color=PALETTE["primary"],
                      annotation_text=f"Weekend {wkend_avg:.1f}%")
        fig.update_layout(plot_bgcolor="#12121f", paper_bgcolor="#12121f",
                          font_color="#e0e0e0", showlegend=False, height=360)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Hour × Day Heatmap**")
    day_hour = (
        dff.groupby(["day_name","hour"])["order_id"].count()
           .reset_index(name="orders")
    )
    pivot = (day_hour.pivot(index="day_name", columns="hour", values="orders")
                     .reindex(dow_order).fillna(0))
    fig = px.imshow(pivot, color_continuous_scale="YlOrRd",
                    labels=dict(x="Hour of Day", y="", color="Orders"),
                    aspect="auto", title="Orders Heatmap — Hour x Day of Week")
    fig.update_layout(plot_bgcolor="#12121f", paper_bgcolor="#12121f",
                      font_color="#e0e0e0", height=320)
    st.plotly_chart(fig, use_container_width=True)

# ── TAB 3: City Cohorts ───────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-header">City Cohort Analysis</div>',
                unsafe_allow_html=True)

    city_hour_all   = df.groupby(["city","hour"])["order_id"].count().unstack(fill_value=0)
    city_hour_share = city_hour_all.div(city_hour_all.sum(axis=1), axis=0)
    lunch_share     = city_hour_share[[12,13]].sum(axis=1)
    dinner_share    = city_hour_share[[19,20,21]].sum(axis=1)

    city_stats = df.groupby("city").agg(
        volume=("order_id","count"),
        avg_value=("order_value","mean"),
        surge_rate=("surge_applied","mean"),
    ).round(2)
    city_stats["dinner_lunch_ratio"] = (dinner_share / lunch_share).round(2)

    def cohort_label(v):
        if v >= tier1_min: return "Tier 1 — Scale"
        if v >= tier2_min: return "Tier 2 — Growth"
        return "Tier 3 — Emerging"

    city_stats["cohort"] = city_stats["volume"].apply(cohort_label)
    city_stats = city_stats.sort_values("volume", ascending=False)
    top_cuisine = (
        df.groupby(["city","cuisine"])["order_id"].count()
          .reset_index().sort_values("order_id",ascending=False)
          .groupby("city").first()["cuisine"]
    )
    city_stats["top_cuisine"] = top_cuisine

    col1, col2 = st.columns(2)
    with col1:
        fig = px.scatter(
            city_stats.reset_index(), x="volume", y="dinner_lunch_ratio",
            size="avg_value", color="cohort",
            color_discrete_map={
                "Tier 1 — Scale":    PALETTE["primary"],
                "Tier 2 — Growth":   PALETTE["accent"],
                "Tier 3 — Emerging": PALETTE["neutral"],
            },
            text="city",
            labels={"volume":"Total Orders","dinner_lunch_ratio":"Dinner/Lunch Ratio"},
            title="Volume vs Demand Skew  (size = avg order value)",
            hover_data={"top_cuisine":True,"surge_rate":True})
        fig.update_traces(textposition="top center")
        fig.update_layout(plot_bgcolor="#12121f", paper_bgcolor="#12121f",
                          font_color="#e0e0e0", height=420)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        ratio_df = city_stats[["dinner_lunch_ratio","cohort"]].reset_index()
        ratio_df = ratio_df.sort_values("dinner_lunch_ratio",ascending=False)
        avg_r = city_stats["dinner_lunch_ratio"].mean()
        fig = px.bar(ratio_df, x="city", y="dinner_lunch_ratio", color="cohort",
                     color_discrete_map={
                         "Tier 1 — Scale":    PALETTE["primary"],
                         "Tier 2 — Growth":   PALETTE["accent"],
                         "Tier 3 — Emerging": PALETTE["neutral"],
                     },
                     text_auto=".2f",
                     title="Dinner-to-Lunch Ratio by City",
                     labels={"city":"","dinner_lunch_ratio":"Dinner/Lunch"})
        fig.add_hline(y=avg_r, line_dash="dash", line_color="white",
                      annotation_text=f"Avg {avg_r:.2f}x")
        fig.update_layout(plot_bgcolor="#12121f", paper_bgcolor="#12121f",
                          font_color="#e0e0e0", showlegend=False,
                          yaxis=dict(range=[1.2,1.8]), height=420)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Normalised Hourly Profile**")
    profile_df = (city_hour_share.reset_index()
                   .melt(id_vars="city", var_name="hour", value_name="share"))
    profile_df["share_%"] = profile_df["share"] * 100
    profile_df = profile_df[profile_df["city"].isin(selected_cities)]
    fig = px.line(profile_df, x="hour", y="share_%", color="city",
                  color_discrete_map=CITY_COLORS, markers=True,
                  labels={"hour":"Hour of Day","share_%":"% of Daily Orders","city":"City"},
                  title="Normalised Demand Profile — same shape, different dinner-lunch skew")
    fig.add_vrect(x0=11.5, x1=14, fillcolor=PALETTE["primary"],  opacity=0.08, line_width=0)
    fig.add_vrect(x0=18.5, x1=22, fillcolor=PALETTE["secondary"],opacity=0.08, line_width=0)
    fig.update_layout(plot_bgcolor="#12121f", paper_bgcolor="#12121f",
                      font_color="#e0e0e0", height=380,
                      xaxis=dict(tickmode="linear", dtick=1, gridcolor="#2a2a3e"),
                      yaxis=dict(gridcolor="#2a2a3e"))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**City Summary Table**")
    disp = city_stats[["cohort","volume","avg_value","surge_rate",
                         "dinner_lunch_ratio","top_cuisine"]].copy()
    disp.columns = ["Cohort","Orders","Avg Rs.","Surge Rate","D/L Ratio","Top Cuisine"]
    disp["Surge Rate"] = disp["Surge Rate"].apply(lambda x: f"{x*100:.1f}%")
    st.dataframe(disp, use_container_width=True)

# ── TAB 4: Cuisine ────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-header">Cuisine Demand Analysis</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        cuisine_vol = (
            dff.groupby("cuisine")["order_id"].count()
               .reset_index(name="orders")
               .sort_values("orders", ascending=True)
        )
        fig = px.bar(cuisine_vol, x="orders", y="cuisine", orientation="h",
                     color="orders", color_continuous_scale="YlOrRd",
                     title="Orders by Cuisine",
                     labels={"cuisine":"","orders":"Orders"})
        fig.update_layout(plot_bgcolor="#12121f", paper_bgcolor="#12121f",
                          font_color="#e0e0e0", coloraxis_showscale=False, height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        cc = (df[df["city"].isin(selected_cities)]
                .groupby(["city","cuisine"])["order_id"].count()
                .unstack(fill_value=0))
        cc_pct = cc.div(cc.sum(axis=1),axis=0) * 100
        fig = px.imshow(cc_pct.round(1), color_continuous_scale="YlOrRd",
                        text_auto=".0f",
                        labels=dict(x="Cuisine", y="City", color="% orders"),
                        title="Cuisine Mix — city identity heatmap", aspect="auto")
        fig.update_layout(plot_bgcolor="#12121f", paper_bgcolor="#12121f",
                          font_color="#e0e0e0", height=380)
        st.plotly_chart(fig, use_container_width=True)

    cuisine_hour = (
        dff.groupby(["cuisine","hour"])["order_id"].count()
           .reset_index(name="orders")
    )
    fig = px.line(cuisine_hour, x="hour", y="orders", color="cuisine", markers=True,
                  title="Orders by Hour for Each Cuisine",
                  labels={"hour":"Hour of Day","orders":"Orders","cuisine":"Cuisine"})
    fig.add_vrect(x0=11.5, x1=14, fillcolor=PALETTE["primary"],  opacity=0.07, line_width=0)
    fig.add_vrect(x0=18.5, x1=22, fillcolor=PALETTE["secondary"],opacity=0.07, line_width=0)
    fig.update_layout(plot_bgcolor="#12121f", paper_bgcolor="#12121f",
                      font_color="#e0e0e0", height=380,
                      xaxis=dict(tickmode="linear", dtick=1, gridcolor="#2a2a3e"),
                      yaxis=dict(gridcolor="#2a2a3e"))
    st.plotly_chart(fig, use_container_width=True)

# ── TAB 5: Surge Waste ────────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-header">Surge Waste Calculator</div>',
                unsafe_allow_html=True)
    st.info(f"Using surge incentive = **Rs.{surge_cost}/order** (adjust in sidebar). "
            f"Analysis covers **{n_days} days** of filtered data.")

    hgroups = {
        "Dinner (19-21)  HIGH demand  [Justified]":        [19,20,21],
        "Lunch (12-13)   MID demand   [Justified]":        [12,13],
        "Transition (10-11, 14-18)  MODEST [Partial]":    [10,11,14,15,16,17,18],
        "Night (0-9, 22-23)  LOW demand  [WASTED]":        list(range(0,10))+[22,23],
    }
    rows = []
    for label, hours in hgroups.items():
        sub = dff[dff["hour"].isin(hours)]
        tot = len(sub); sur = int(sub["surge_applied"].sum())
        rows.append({
            "Hour Block": label,
            "Total Orders": f"{tot:,}",
            "Surge Orders": f"{sur:,}",
            "Surge %":      f"{sur/tot*100:.1f}%",
            f"Cost ({n_days}d) Rs.": f"{sur*surge_cost:,.0f}",
            "Monthly Cost Rs.":      f"{sur*surge_cost*(30/n_days):,.0f}",
        })

    def highlight(row):
        if "WASTED" in row["Hour Block"]:   return ["background-color:#3a1a1a"]*len(row)
        if "Partial" in row["Hour Block"]:  return ["background-color:#2a2a1a"]*len(row)
        return [""]*len(row)

    st.dataframe(pd.DataFrame(rows).style.apply(highlight, axis=1),
                 hide_index=True, use_container_width=True)

    off_peak = dff[dff["hour"].isin(list(range(0,10))+[22,23])]["surge_applied"].sum()
    trans    = dff[dff["hour"].isin([10,11,14,15,16,17,18])]["surge_applied"].sum()
    save_off  = off_peak * surge_cost * (30/n_days)
    save_trans = trans  * surge_cost * 0.5 * (30/n_days)

    c1,c2,c3 = st.columns(3)
    kpi(c1, "Monthly saving (time-box surge)",      f"Rs.{save_off:,.0f}",   "off-peak surge removed", True)
    kpi(c2, "Additional saving (halve transition)", f"Rs.{save_trans:,.0f}", "partial 10-11, 14-18",   True)
    kpi(c3, "Total potential monthly saving",       f"Rs.{save_off+save_trans:,.0f}", "both recs", True)

    st.divider()
    surge_hourly = (
        dff.groupby("hour")
           .agg(surge_orders=("surge_applied","sum"),
                total_orders=("order_id","count"))
           .reset_index()
    )
    surge_hourly["is_waste"] = surge_hourly["hour"].isin(list(range(0,10))+[22,23])
    fig = px.bar(surge_hourly, x="hour", y="surge_orders", color="is_waste",
                 color_discrete_map={True:"#FF5252", False:PALETTE["neutral"]},
                 labels={"hour":"Hour","surge_orders":"Surge Orders","is_waste":"Off-Peak Waste"},
                 title="Surge Orders by Hour — Red = Off-Peak Waste", text_auto=True)
    fig.update_layout(plot_bgcolor="#12121f", paper_bgcolor="#12121f",
                      font_color="#e0e0e0", height=380,
                      xaxis=dict(tickmode="linear", dtick=1, gridcolor="#2a2a3e"),
                      yaxis=dict(gridcolor="#2a2a3e"))
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.markdown(
    "<div style='text-align:center;color:#555;font-size:12px'>"
    "Case 3 — Food Delivery Demand Pulse · Jan–Mar 2025 · 50,000 orders"
    "</div>", unsafe_allow_html=True)
