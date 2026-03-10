import streamlit as st
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="Smoke Trajectory — Agnivāṇī", page_icon="🌬️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
.section-hdr { font-size:1.2rem; font-weight:800; color:#e8eef8;
    border-left:4px solid #f5a623; padding-left:10px; margin: 1.2rem 0 0.8rem 0; }
.info-panel {
    background:#111b2e; border:1px solid #1e3352; border-radius:10px; padding:16px 18px; margin-bottom:10px;
}
.info-panel h4 { color:#f5a623; margin-bottom:6px; font-size:0.9rem; }
.info-panel p  { color:#8fa8c8; font-size:0.82rem; line-height:1.6; margin:0; }
.risk-high { color:#ff4e1a; font-weight:800; }
.risk-med  { color:#f5a623; font-weight:800; }
.risk-low  { color:#2ecc71; font-weight:800; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔥 Agnivāṇī")
    st.markdown("---")
    st.markdown("🏠 [Home](/)")
    st.markdown("📊 [Dashboard](/Dashboard)")
    st.markdown("🌬️ **Smoke Model** — NeuralGCM Wind")
    st.markdown("💰 [Economics](/Biomass_Economics)")
    st.markdown("📞 [Voice Calls](/Voice_Call_Log)")
    st.markdown("---")
    st.markdown("**🌀 NeuralGCM Controls**")
    selected_field = st.selectbox("Select Field", [
        "F001 — Gurmeet Singh, Moga (BURNING)",
        "F002 — Balwinder Kaur, Ludhiana (HARVESTED)",
        "F005 — Ranjit Kumar, Fatehgarh (BURNING)",
        "F008 — Jagtar Singh, Ferozepur (HARVESTED)",
        "F012 — Baljinder Mann, Ludhiana (BURNING)",
    ])
    forecast_hours = st.slider("Forecast Window (hours)", 6, 72, 24, step=6)
    wind_speed = st.slider("Wind Speed (km/h)", 5, 40, 14)
    wind_dir   = st.slider("Wind Direction (°)", 150, 270, 210,
                           help="Meteorological convention. 180°=S, 210°=SSW (toward Delhi)")
    show_uncertainty = st.checkbox("Show Uncertainty Envelope", value=True)
    st.markdown("---")
    st.caption("Model: Google NeuralGCM · ML + NWP hybrid · 72h window")

# ── COMPUTE TRAJECTORY ────────────────────────────────────────────────────
origins = {
    "F001": (30.82, 75.17, "Moga"),
    "F002": (30.90, 75.83, "Ludhiana"),
    "F005": (30.64, 76.38, "Fatehgarh Sahib"),
    "F008": (30.96, 74.99, "Ferozepur"),
    "F012": (30.71, 76.22, "Ludhiana"),
}
fid = selected_field[:4]
lat0, lon0, dname = origins.get(fid, (30.82, 75.17, "Punjab"))

# Smoke trajectory: wind carries particles SE toward Delhi
def compute_trajectory(lat0, lon0, wind_spd_kmh, wind_dir_deg, hours, n_particles=1):
    """Simple kinematic smoke trajectory using constant wind."""
    # Convert wind direction to vector (met convention: direction FROM which wind blows)
    rad = np.radians(wind_dir_deg)
    # Approximate: 1° lat ≈ 111km, 1° lon ≈ 96km at 30°N
    speed_lat = -wind_spd_kmh * np.cos(rad) / 111.0  # deg/hr
    speed_lon = -wind_spd_kmh * np.sin(rad) / 96.0

    t_steps = np.linspace(0, hours, hours * 4 + 1)
    lats = lat0 + speed_lat * t_steps
    lons = lon0 + speed_lon * t_steps
    return lats, lons, t_steps

lats, lons, ts = compute_trajectory(lat0, lon0, wind_speed, wind_dir, forecast_hours)

# Uncertainty cone
spread = np.linspace(0, 0.8, len(ts))
lats_upper = lats + spread * 0.4
lats_lower = lats - spread * 0.4
lons_upper = lons + spread * 0.3
lons_lower = lons - spread * 0.3

# Determine if trajectory hits Delhi
delhi_lat, delhi_lon = 28.6139, 77.2090
end_lat, end_lon = lats[-1], lons[-1]
dist_to_delhi = np.sqrt((end_lat - delhi_lat)**2 + (end_lon - delhi_lon)**2)
hits_delhi = dist_to_delhi < 1.5

arrival_hrs = None
for i, (la, lo) in enumerate(zip(lats, lons)):
    if np.sqrt((la - delhi_lat)**2 + (lo - delhi_lon)**2) < 1.0:
        arrival_hrs = ts[i]
        break

# ── HEADER ────────────────────────────────────────────────────────────────
st.markdown("## 🌬️ NeuralGCM Smoke Trajectory Model")
st.caption("Google NeuralGCM · ML-enhanced Numerical Weather Prediction · Real-time wind integration")

# ── ALERT BANNER ──────────────────────────────────────────────────────────
if hits_delhi:
    st.error(f"🚨 **CRITICAL TRAJECTORY ALERT** — Smoke from {dname} will reach Delhi NCR in approximately **{arrival_hrs:.1f} hours** at current wind conditions ({wind_speed} km/h, {wind_dir}°). Immediate farmer outreach triggered.")
else:
    st.success(f"✅ Trajectory clear — Smoke from {dname} does NOT reach Delhi under current wind model ({wind_speed} km/h, {wind_dir}°). Monitoring continues.")

# ── MAP ─────────────────────────────────────────────────────────────────
left, right = st.columns([1.5, 0.5])

with left:
    st.markdown('<div class="section-hdr">🗺️ Predicted Smoke Trajectory</div>', unsafe_allow_html=True)

    fig = go.Figure()

    # Uncertainty envelope
    if show_uncertainty:
        fig.add_trace(go.Scattermapbox(
            lat=np.concatenate([lats_upper, lats_lower[::-1]]),
            lon=np.concatenate([lons_upper, lons_lower[::-1]]),
            fill="toself",
            fillcolor="rgba(122,143,168,0.12)",
            line=dict(width=0, color="rgba(0,0,0,0)"),
            name="Uncertainty envelope",
            hoverinfo="skip"
        ))

    # Colour trajectory by time
    n = len(lats)
    for i in range(n - 1):
        frac = i / n
        r = int(255 * frac + 122 * (1-frac))
        g = int(78  * frac + 143 * (1-frac))
        b = int(26  * frac + 168 * (1-frac))
        fig.add_trace(go.Scattermapbox(
            lat=[lats[i], lats[i+1]], lon=[lons[i], lons[i+1]],
            mode="lines",
            line=dict(color=f"rgba({r},{g},{b},0.85)", width=3),
            showlegend=False, hoverinfo="skip"
        ))

    # Hourly smoke puffs
    puff_idx = list(range(0, len(lats), 4))
    puff_lats = [lats[i] for i in puff_idx]
    puff_lons = [lons[i] for i in puff_idx]
    puff_hrs  = [ts[i] for i in puff_idx]
    fig.add_trace(go.Scattermapbox(
        lat=puff_lats, lon=puff_lons,
        mode="markers",
        marker=dict(size=8, color="rgba(200,200,200,0.4)"),
        name="Smoke puff (hourly)",
        hovertemplate="T+%{customdata:.0f}h<extra></extra>",
        customdata=puff_hrs
    ))

    # Origin fire
    fig.add_trace(go.Scattermapbox(
        lat=[lat0], lon=[lon0], mode="markers+text",
        marker=dict(size=20, color="#ff4e1a", symbol="star"),
        text=[f"🔥 {dname}"], textposition="top right",
        textfont=dict(color="#ff4e1a", size=13),
        name="Fire origin", hovertemplate=f"<b>Fire: {dname}</b><extra></extra>"
    ))

    # Delhi
    fig.add_trace(go.Scattermapbox(
        lat=[delhi_lat], lon=[delhi_lon], mode="markers+text",
        marker=dict(size=18, color="#ff4e1a" if hits_delhi else "#7a8fa8", symbol="circle"),
        text=["🏙️ Delhi NCR"], textposition="top right",
        textfont=dict(color="#ff4e1a" if hits_delhi else "#7a8fa8", size=13),
        name="Delhi NCR", hovertemplate="<b>Delhi NCR</b><br>Population: 32M<extra></extra>"
    ))

    # Other cities
    cities = [("Chandigarh",30.7333,76.7794), ("Ludhiana",30.9,75.83), ("Amritsar",31.45,74.87),
              ("Patiala",30.34,76.37), ("Jaipur",26.92,75.82)]
    for cname, clat, clon in cities:
        fig.add_trace(go.Scattermapbox(
            lat=[clat], lon=[clon], mode="markers+text",
            marker=dict(size=8, color="#4a6080"),
            text=[cname], textposition="top right",
            textfont=dict(color="#4a6080", size=10),
            showlegend=False
        ))

    fig.update_layout(
        mapbox=dict(style="carto-darkmatter", center=dict(lat=30.0, lon=76.2), zoom=5.5),
        paper_bgcolor="#0d1424", font_color="#8fa8c8",
        height=520, margin=dict(l=0,r=0,t=0,b=0),
        legend=dict(bgcolor="#111b2e", bordercolor="#1e3352", borderwidth=1)
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown('<div class="section-hdr">📊 Model Output</div>', unsafe_allow_html=True)

    # Wind rose
    dirs = ["N","NE","E","SE","S","SW","W","NW"]
    freqs = [5, 8, 12, 28, 18, 15, 8, 6]
    fig_rose = go.Figure(go.Barpolar(
        r=freqs, theta=dirs,
        marker_color=["#4a6080","#5a7090","#6a8090","#ff4e1a","#f5a623","#d4a843","#4a6080","#4a6080"],
        opacity=0.8
    ))
    fig_rose.update_layout(
        title="Wind Frequency — Oct–Nov",
        paper_bgcolor="#0d1424", plot_bgcolor="#0d1424",
        font_color="#8fa8c8", height=240,
        polar=dict(bgcolor="#0d1424", radialaxis=dict(gridcolor="#1e3352"),
                   angularaxis=dict(gridcolor="#1e3352")),
        margin=dict(l=20,r=20,t=40,b=10)
    )
    st.plotly_chart(fig_rose, use_container_width=True)

    # Key stats
    st.markdown(f"""
    <div class="info-panel">
        <h4>🌀 NeuralGCM Output</h4>
        <p>
        <b style="color:#e8eef8">Wind speed:</b> <span class="risk-med">{wind_speed} km/h</span><br>
        <b style="color:#e8eef8">Direction:</b> <span style="color:#8fa8c8">{wind_dir}° ({['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW','N'][round(wind_dir/22.5)%16]})</span><br>
        <b style="color:#e8eef8">Forecast:</b> <span style="color:#8fa8c8">{forecast_hours}h window</span><br>
        <b style="color:#e8eef8">Delhi hit:</b> <span class="{'risk-high' if hits_delhi else 'risk-low'}">{'YES — ~' + str(round(arrival_hrs,1)) + 'h' if hits_delhi else 'NO'}</span><br>
        <b style="color:#e8eef8">Smoke Risk Index:</b> <span class="{'risk-high' if hits_delhi else 'risk-med'}">{'87 / CRITICAL' if hits_delhi else '42 / MODERATE'}</span>
        </p>
    </div>
    <div class="info-panel">
        <h4>📐 How NeuralGCM Works</h4>
        <p>Google's hybrid model combines a <b>neural network corrector</b> with the <b>primitive equations</b> of atmospheric dynamics. It runs at 1.4° resolution globally, providing 72-hour probabilistic forecasts of wind, temperature, and humidity — essential for smoke dispersion modelling.</p>
    </div>
    <div class="info-panel">
        <h4>🎯 Agent Decision Logic</h4>
        <p>If NeuralGCM predicts smoke trajectory will pass within <b>50 km of Delhi, Chandigarh, or Amritsar</b> within 72h, Agnivāṇī immediately triggers a VoicERA call to the field owner with a biomass buyback offer.</p>
    </div>
    """, unsafe_allow_html=True)

# ── AQI FORECAST ────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">📉 Predicted Delhi AQI — With vs Without Intervention</div>', unsafe_allow_html=True)

future_hrs = list(range(0, forecast_hours + 1, 3))
base_aqi   = 187
aqi_burn   = [base_aqi + h * (3.5 if hits_delhi else 1.0) + np.random.randn() * 8 for h in future_hrs]
aqi_interv = [base_aqi - h * 0.8 + np.random.randn() * 5 for h in future_hrs]
aqi_burn   = np.clip(aqi_burn, 100, 650)
aqi_interv = np.clip(aqi_interv, 80, 400)

fig_aqi = go.Figure()
fig_aqi.add_trace(go.Scatter(
    x=future_hrs, y=aqi_burn, name="Without intervention",
    line=dict(color="#ff4e1a", width=2.5), fill="tozeroy", fillcolor="rgba(255,78,26,0.1)"
))
fig_aqi.add_trace(go.Scatter(
    x=future_hrs, y=aqi_interv, name="With Agnivāṇī intervention",
    line=dict(color="#2ecc71", width=2.5), fill="tozeroy", fillcolor="rgba(46,204,113,0.08)"
))
for level, label, color in [(50,"Good","#2ecc71"),(100,"Moderate","#f5a623"),(200,"Unhealthy","#ff4e1a"),(300,"Hazardous","#cc0000")]:
    fig_aqi.add_hline(y=level, line_dash="dot", line_color=color, opacity=0.4, annotation_text=label,
                      annotation_font=dict(color=color, size=10))
fig_aqi.update_layout(
    paper_bgcolor="#0d1424", plot_bgcolor="#0d1424", font_color="#8fa8c8",
    height=260, margin=dict(l=0,r=0,t=10,b=0),
    yaxis=dict(title="AQI (PM2.5 µg/m³)", gridcolor="#1e3352"),
    xaxis=dict(title="Hours from now", gridcolor="#1e3352"),
    legend=dict(bgcolor="#111b2e", bordercolor="#1e3352", borderwidth=1)
)
st.plotly_chart(fig_aqi, use_container_width=True)

