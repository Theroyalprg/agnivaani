import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import random
import time

st.set_page_config(page_title="Dashboard — Agnivāṇī", page_icon="📊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
.metric-card {
    background: #111b2e; border: 1px solid #1e3352; border-radius: 10px;
    padding: 16px 18px; text-align: center; margin-bottom: 8px;
}
.metric-val { font-size: 2rem; font-weight: 800; line-height: 1; }
.metric-lbl { font-size: 0.72rem; color: #8fa8c8; letter-spacing: 1px; text-transform: uppercase; margin-top: 4px; }
.field-row {
    background: #111b2e; border: 1px solid #1e3352; border-radius: 8px;
    padding: 12px 16px; margin-bottom: 6px;
    display: flex; align-items: center; justify-content: space-between;
}
.status-pill {
    display: inline-block; padding: 3px 10px; border-radius: 12px;
    font-size: 0.7rem; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;
}
.section-hdr { font-size:1.2rem; font-weight:800; color:#e8eef8;
    border-left:4px solid #f5a623; padding-left:10px; margin: 1.2rem 0 0.8rem 0; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔥 Agnivāṇī")
    st.caption("Nocturnal Biomass-Arbitrage & Smoke-Trajectory Agent")
    st.markdown("---")
    st.markdown("🏠 [Home](/)")
    st.markdown("📊 **Dashboard** — Live Field Monitor")
    st.markdown("🌬️ [Smoke Model](/Smoke_Trajectory)")
    st.markdown("💰 [Economics](/Biomass_Economics)")
    st.markdown("📞 [Voice Calls](/Voice_Call_Log)")
    st.markdown("---")
    st.markdown("**⚙️ Simulation Controls**")
    auto_refresh = st.toggle("Auto-refresh (10s)", value=False)
    if st.button("🔄 Refresh Data"):
        st.rerun()
    st.markdown("---")
    season = st.selectbox("Season", ["Oct–Nov 2024 (Live)", "Oct–Nov 2023", "Oct–Nov 2022"])
    district_filter = st.multiselect(
        "Filter Districts",
        ["All", "Ludhiana", "Amritsar", "Patiala", "Sangrur", "Moga", "Bathinda", "Ferozepur", "Fatehgarh Sahib", "Kapurthala"],
        default=["All"]
    )
    st.caption("Data: Sentinel-3 SLSTR NRT · Google AMED API")

# ── SIMULATED LIVE DATA ───────────────────────────────────────────────────
np.random.seed(int(datetime.now().strftime("%H%M")) % 100)

FIELD_DATA = [
    {"id": "F001", "farmer": "Gurmeet Singh",     "village": "Lohian Khas",  "district": "Moga",           "area_ha": 6.2,  "status": "BURNING",   "harvested_h": 4,  "sri": 87, "lat": 30.82, "lon": 75.17, "wind_deg": 210},
    {"id": "F002", "farmer": "Balwinder Kaur",    "village": "Sahnewal",     "district": "Ludhiana",       "area_ha": 4.8,  "status": "HARVESTED", "harvested_h": 7,  "sri": 72, "lat": 30.90, "lon": 75.83, "wind_deg": 195},
    {"id": "F003", "farmer": "Sukhdev Rana",      "village": "Rajpura",      "district": "Patiala",        "area_ha": 3.1,  "status": "HARVESTED", "harvested_h": 12, "sri": 58, "lat": 30.48, "lon": 76.59, "wind_deg": 215},
    {"id": "F004", "farmer": "Harpreet Gill",     "village": "Tarn Taran",   "district": "Amritsar",       "area_ha": 8.4,  "status": "MONITORING","harvested_h": 18, "sri": 43, "lat": 31.45, "lon": 74.93, "wind_deg": 200},
    {"id": "F005", "farmer": "Ranjit Kumar",      "village": "Sirhind",      "district": "Fatehgarh Sahib","area_ha": 2.7,  "status": "BURNING",   "harvested_h": 6,  "sri": 79, "lat": 30.64, "lon": 76.38, "wind_deg": 205},
    {"id": "F006", "farmer": "Daljeet Sandhu",    "village": "Dhuri",        "district": "Sangrur",        "area_ha": 5.1,  "status": "BOOKED",    "harvested_h": 24, "sri": 0,  "lat": 30.05, "lon": 75.87, "wind_deg": 220},
    {"id": "F007", "farmer": "Manpreet Dhaliwal", "village": "Rampura Phul", "district": "Bathinda",       "area_ha": 7.3,  "status": "DELIVERED", "harvested_h": 36, "sri": 0,  "lat": 30.27, "lon": 75.22, "wind_deg": 210},
    {"id": "F008", "farmer": "Jagtar Singh",      "village": "Zira",         "district": "Ferozepur",      "area_ha": 4.0,  "status": "HARVESTED", "harvested_h": 2,  "sri": 61, "lat": 30.96, "lon": 74.99, "wind_deg": 200},
    {"id": "F009", "farmer": "Kirpal Brar",       "village": "Phagwara",     "district": "Kapurthala",     "area_ha": 6.6,  "status": "MONITORING","harvested_h": 20, "sri": 38, "lat": 31.22, "lon": 75.77, "wind_deg": 195},
    {"id": "F010", "farmer": "Amarjit Dhillon",   "village": "Barnala",      "district": "Sangrur",        "area_ha": 5.5,  "status": "HARVESTED", "harvested_h": 10, "sri": 65, "lat": 30.38, "lon": 75.54, "wind_deg": 208},
    {"id": "F011", "farmer": "Surjit Kaur",       "village": "Malerkotla",   "district": "Sangrur",        "area_ha": 3.8,  "status": "BOOKED",    "harvested_h": 30, "sri": 0,  "lat": 30.53, "lon": 75.88, "wind_deg": 215},
    {"id": "F012", "farmer": "Baljinder Mann",    "village": "Khanna",       "district": "Ludhiana",       "area_ha": 7.1,  "status": "BURNING",   "harvested_h": 5,  "sri": 82, "lat": 30.71, "lon": 76.22, "wind_deg": 200},
]

df = pd.DataFrame(FIELD_DATA)

# ── HEADER ───────────────────────────────────────────────────────────────
st.markdown("## 📊 Agnivāṇī — Live Field Dashboard")
st.caption(f"⏱ Last updated: {datetime.now().strftime('%d %b %Y, %H:%M:%S IST')}  ·  Season: {season}")

# ── KPI METRICS ───────────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)
total     = len(df)
burning   = len(df[df.status == "BURNING"])
harvested = len(df[df.status == "HARVESTED"])
booked    = len(df[df.status == "BOOKED"])
delivered = len(df[df.status == "DELIVERED"])
revenue   = sum(r["area_ha"] * 2.5 * 2400 for _, r in df[df.status.isin(["BOOKED","DELIVERED"])].iterrows())

for col, val, label, color in zip(
    [c1, c2, c3, c4, c5, c6],
    [total, burning, harvested, booked, delivered, f"₹{revenue/100000:.1f}L"],
    ["Fields Monitored", "Active Burns 🔥", "Recently Harvested", "Trucks Booked", "Delivered", "Revenue Generated"],
    ["#e8eef8", "#ff4e1a", "#f5a623", "#2ecc71", "#d4a843", "#2ecc71"]
):
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-val" style="color:{color}">{val}</div>
        <div class="metric-lbl">{label}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── MAP + TABLE ─────────────────────────────────────────────────────────
left_col, right_col = st.columns([1.3, 0.7])

with left_col:
    st.markdown('<div class="section-hdr">🗺️ Sentinel-3 SLSTR Field Map — Punjab / Haryana</div>', unsafe_allow_html=True)

    status_config = {
        "BURNING":   {"color": "#ff4e1a", "size": 22, "symbol": "star"},
        "HARVESTED": {"color": "#f5a623", "size": 14, "symbol": "circle"},
        "MONITORING":{"color": "#7a8fa8", "size": 12, "symbol": "circle"},
        "BOOKED":    {"color": "#2ecc71", "size": 14, "symbol": "diamond"},
        "DELIVERED": {"color": "#1a7a42", "size": 14, "symbol": "diamond"},
    }

    fig_map = go.Figure()

    # Wind vectors
    for _, r in df.iterrows():
        angle_rad = np.radians(r["wind_deg"])
        dlat = 0.4 * np.cos(angle_rad)
        dlon = 0.4 * np.sin(angle_rad)
        fig_map.add_trace(go.Scattermapbox(
            lat=[r["lat"], r["lat"] + dlat],
            lon=[r["lon"], r["lon"] + dlon],
            mode="lines",
            line=dict(color="rgba(122,143,168,0.25)", width=1),
            showlegend=False, hoverinfo="skip"
        ))

    for status, cfg in status_config.items():
        sub = df[df.status == status]
        if len(sub) == 0:
            continue
        fig_map.add_trace(go.Scattermapbox(
            lat=sub["lat"], lon=sub["lon"],
            mode="markers",
            marker=dict(size=cfg["size"], color=cfg["color"],
                        opacity=0.9 if status == "BURNING" else 0.75),
            name=status,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Village: %{customdata[1]}<br>"
                "District: %{customdata[2]}<br>"
                "Area: %{customdata[3]} ha<br>"
                "SRI: %{customdata[4]}<br>"
                "<extra></extra>"
            ),
            customdata=sub[["farmer","village","district","area_ha","sri"]].values,
        ))

    # Delhi marker
    fig_map.add_trace(go.Scattermapbox(
        lat=[28.6139], lon=[77.2090], mode="markers+text",
        marker=dict(size=16, color="#ff4e1a", symbol="star"),
        text=["Delhi NCR"], textposition="top right",
        textfont=dict(color="#ff4e1a", size=12),
        name="Delhi (AQI Impact Zone)", showlegend=True,
        hovertemplate="<b>Delhi NCR</b><br>Primary smoke destination<extra></extra>"
    ))

    fig_map.update_layout(
        mapbox=dict(
            style="carto-darkmatter",
            center=dict(lat=30.8, lon=75.8),
            zoom=6.5
        ),
        paper_bgcolor="#0d1424",
        font_color="#8fa8c8",
        height=480,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            bgcolor="#111b2e", bordercolor="#1e3352", borderwidth=1,
            font=dict(size=11)
        )
    )
    st.plotly_chart(fig_map, use_container_width=True)

with right_col:
    st.markdown('<div class="section-hdr">📋 Field Status Log</div>', unsafe_allow_html=True)

    status_colors = {
        "BURNING":   ("#ff4e1a", "rgba(255,78,26,0.12)"),
        "HARVESTED": ("#f5a623", "rgba(245,166,35,0.1)"),
        "MONITORING":("#7a8fa8", "rgba(122,143,168,0.08)"),
        "BOOKED":    ("#2ecc71", "rgba(46,204,113,0.1)"),
        "DELIVERED": ("#1a7a42", "rgba(26,122,66,0.1)"),
    }

    status_icons = {
        "BURNING": "🔥", "HARVESTED": "🌾", "MONITORING": "🛰️",
        "BOOKED": "🚛", "DELIVERED": "✅"
    }

    for _, row in df.iterrows():
        c, bg = status_colors[row["status"]]
        icon  = status_icons[row["status"]]
        st.markdown(f"""
        <div style="background:{bg};border:1px solid {c}33;border-radius:8px;
                    padding:10px 14px;margin-bottom:7px;border-left:3px solid {c}">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="font-size:0.85rem;font-weight:700;color:#e8eef8">{row['farmer']}</span>
                <span style="background:{c}22;color:{c};font-size:0.65rem;font-weight:700;
                             padding:2px 8px;border-radius:10px;letter-spacing:1px">{icon} {row['status']}</span>
            </div>
            <div style="font-size:0.75rem;color:#8fa8c8;margin-top:3px">
                {row['village']}, {row['district']} · {row['area_ha']} ha
            </div>
            <div style="display:flex;justify-content:space-between;margin-top:4px">
                <span style="font-size:0.72rem;color:#4a6080">Harvested {row['harvested_h']}h ago</span>
                <span style="font-size:0.72rem;color:{'#ff4e1a' if row['sri'] > 70 else '#f5a623' if row['sri'] > 40 else '#2ecc71'}">
                    SRI: {row['sri']}
                </span>
            </div>
        </div>""", unsafe_allow_html=True)

# ── TIMESERIES ──────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">📈 Hourly Fire Detection — Last 24 Hours (Sentinel-3 Passes)</div>', unsafe_allow_html=True)

hours = [(datetime.now() - timedelta(hours=23-i)) for i in range(24)]
np.random.seed(42)
detections = np.clip(np.random.poisson(3, 24) + np.array([0]*12 + [2,4,6,5,4,3,2,1,1,1,1,0]), 0, 15)
aqi_vals   = 180 + np.cumsum(np.random.randn(24)*5) + detections * 8

fig_ts = go.Figure()
fig_ts.add_trace(go.Scatter(
    x=hours, y=detections,
    name="Fire Detections", line=dict(color="#ff4e1a", width=2.5),
    fill="tozeroy", fillcolor="rgba(255,78,26,0.12)",
    yaxis="y1"
))
fig_ts.add_trace(go.Scatter(
    x=hours, y=aqi_vals,
    name="Delhi AQI (est.)", line=dict(color="#8fa8c8", width=1.5, dash="dot"),
    yaxis="y2"
))
fig_ts.add_trace(go.Scatter(
    x=hours, y=[4]*24,
    name="Alert Threshold", line=dict(color="#f5a623", width=1, dash="dash"),
    yaxis="y1"
))
fig_ts.update_layout(
    paper_bgcolor="#0d1424", plot_bgcolor="#0d1424", font_color="#8fa8c8",
    height=220, margin=dict(l=0,r=0,t=10,b=0),
    yaxis=dict(title="Fire Count", gridcolor="#1e3352", side="left"),
    yaxis2=dict(title="AQI", overlaying="y", side="right", gridcolor="#1e3352"),
    legend=dict(bgcolor="#111b2e", bordercolor="#1e3352", borderwidth=1, orientation="h", y=1.02),
    xaxis=dict(gridcolor="#1e3352"),
)
st.plotly_chart(fig_ts, use_container_width=True)

# ── STATUS BREAKDOWN ──────────────────────────────────────────────────────
col_p1, col_p2, col_p3 = st.columns(3)

with col_p1:
    status_counts = df["status"].value_counts().reset_index()
    fig_pie = go.Figure(go.Pie(
        labels=status_counts["status"], values=status_counts["count"],
        marker_colors=["#ff4e1a","#f5a623","#7a8fa8","#2ecc71","#1a7a42"],
        hole=0.5, textinfo="label+percent"
    ))
    fig_pie.update_layout(title="Field Status Breakdown",
        paper_bgcolor="#0d1424", font_color="#8fa8c8", height=280, margin=dict(l=0,r=0,t=40,b=0),
        showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_p2:
    district_burns = df[df.status=="BURNING"].groupby("district").size().reset_index(name="count")
    fig_b = go.Figure(go.Bar(
        x=district_burns["district"], y=district_burns["count"],
        marker_color="#ff4e1a", text=district_burns["count"], textposition="outside"
    ))
    fig_b.update_layout(title="Active Burns by District",
        paper_bgcolor="#0d1424", plot_bgcolor="#0d1424", font_color="#8fa8c8",
        height=280, margin=dict(l=0,r=0,t=40,b=0),
        yaxis=dict(gridcolor="#1e3352"), xaxis=dict(gridcolor="#1e3352"))
    st.plotly_chart(fig_b, use_container_width=True)

with col_p3:
    sri_vals = df[df.sri > 0]["sri"]
    fig_hist = go.Figure(go.Histogram(
        x=sri_vals, nbinsx=8,
        marker_color="#f5a623", opacity=0.8
    ))
    fig_hist.update_layout(title="Smoke Risk Index Distribution",
        paper_bgcolor="#0d1424", plot_bgcolor="#0d1424", font_color="#8fa8c8",
        height=280, margin=dict(l=0,r=0,t=40,b=0),
        yaxis=dict(gridcolor="#1e3352"), xaxis=dict(title="SRI Score", gridcolor="#1e3352"))
    st.plotly_chart(fig_hist, use_container_width=True)

if auto_refresh:
    time.sleep(10)
    st.rerun()

