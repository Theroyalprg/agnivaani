import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="Agnivāṇī — Nocturnal Biomass Arbitrage Agent",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }

.hero-title {
    font-size: 3.2rem; font-weight: 800; letter-spacing: -1px;
    background: linear-gradient(90deg, #f5a623, #ff4e1a);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    line-height: 1.1; margin-bottom: 0.2rem;
}
.hero-sub {
    font-size: 1.05rem; color: #8fa8c8; letter-spacing: 2px;
    text-transform: uppercase; margin-bottom: 1.5rem;
}
.tag-pill {
    display: inline-block; padding: 4px 12px; border-radius: 20px;
    font-size: 0.75rem; font-weight: 700; letter-spacing: 1px;
    margin: 3px; text-transform: uppercase;
}
.tag-free  { background: rgba(46,204,113,0.15); color: #2ecc71; border: 1px solid #1a7a42; }
.tag-ai    { background: rgba(245,166,35,0.12); color: #f5a623; border: 1px solid #c47d10; }
.tag-india { background: rgba(122,143,168,0.12); color: #8fa8c8; border: 1px solid #4a6080; }

.kpi-card {
    background: #111b2e; border: 1px solid #1e3352; border-radius: 12px;
    padding: 20px 18px; text-align: center;
}
.kpi-val  { font-size: 2.4rem; font-weight: 800; line-height: 1; }
.kpi-label { font-size: 0.75rem; color: #8fa8c8; letter-spacing: 1px; text-transform: uppercase; margin-top: 4px; }

.section-header {
    font-size: 1.4rem; font-weight: 800; color: #e8eef8;
    border-left: 4px solid #f5a623; padding-left: 12px;
    margin: 2rem 0 1rem 0;
}
.info-box {
    background: #111b2e; border: 1px solid #1e3352; border-radius: 10px;
    padding: 18px 20px; margin-bottom: 12px;
}
.info-box h4 { color: #f5a623; margin-bottom: 6px; font-size: 0.95rem; }
.info-box p  { color: #8fa8c8; font-size: 0.88rem; line-height: 1.6; margin: 0; }

.flow-step {
    background: linear-gradient(135deg, #111b2e, #0d1424);
    border: 1px solid #1e3352; border-radius: 10px;
    padding: 16px; margin-bottom: 10px; position: relative;
}
.flow-num {
    font-size: 2rem; font-weight: 800; color: #1e3352;
    position: absolute; top: 10px; right: 14px;
}
.flow-step h4 { color: #f5a623; margin-bottom: 4px; font-size: 0.9rem; }
.flow-step p  { color: #8fa8c8; font-size: 0.82rem; margin: 0; line-height: 1.5; }

.quote-box {
    background: linear-gradient(135deg, #0d1a0d, #070b07);
    border: 1px solid #1a5c1a; border-left: 4px solid #2ecc71;
    border-radius: 8px; padding: 18px 20px; margin: 16px 0;
    font-style: italic; color: #a8d8a8; font-size: 0.9rem; line-height: 1.8;
}
.quote-box strong { color: #2ecc71; font-style: normal; }

.source-tag { font-size: 0.7rem; color: #4a6080; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔥 Agnivāṇī")
    st.caption("Nocturnal Biomass-Arbitrage & Smoke-Trajectory Agent")
    st.markdown("---")
    st.markdown("**Navigation**")
    st.markdown("🏠 **Home** — Concept & Architecture")
    st.markdown("📊 [Dashboard](/Dashboard) — Live Field Monitor")
    st.markdown("🌬️ [Smoke Model](/Smoke_Trajectory) — NeuralGCM Wind")
    st.markdown("💰 [Economics](/Biomass_Economics) — Arbitrage Engine")
    st.markdown("📞 [Voice Calls](/Voice_Call_Log) — Bhashini Log")
    st.markdown("---")
    st.caption("Data: Sentinel-3 SLSTR · Google AMED · NeuralGCM · Bhashini VoicERA")

# ── HERO ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">Agnivāṇī 🔥</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Nocturnal Biomass-Arbitrage &amp; Smoke-Trajectory Agent · Northwestern Indian Agricultural Belt</div>', unsafe_allow_html=True)

st.markdown("""
<span class="tag-pill tag-free">100% Free APIs</span>
<span class="tag-pill tag-ai">Multi-AI Fusion</span>
<span class="tag-pill tag-india">Made for India</span>
<span class="tag-pill tag-free">Autonomous Agent</span>
<span class="tag-pill tag-ai">Circular Economy</span>
<span class="tag-pill tag-india">Punjabi · Haryanvi</span>
""", unsafe_allow_html=True)

st.markdown("---")

# ── KPI ROW ──────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
kpis = [
    ("35M", "Tonnes stubble burned annually", "#f5a623"),
    ("~700", "µg/m³ Delhi PM2.5 peak (Nov)", "#ff4e1a"),
    ("₹2,400", "Per tonne Bio-CNG price", "#2ecc71"),
    ("72h", "NeuralGCM forecast window", "#8fa8c8"),
    ("0", "Cost to farmers for calls", "#d4a843"),
]
for col, (val, label, color) in zip([k1,k2,k3,k4,k5], kpis):
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-val" style="color:{color}">{val}</div>
        <div class="kpi-label">{label}</div>
    </div>""", unsafe_allow_html=True)

# ── THE PROBLEM ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">The Problem: Stubble Burning Crisis</div>', unsafe_allow_html=True)

col_a, col_b = st.columns([1.1, 0.9])

with col_a:
    st.markdown("""
    Every October–November, after the **kharif (rice) harvest**, farmers across Punjab and Haryana
    face a 2–3 week window to clear their fields before the next wheat sowing. With no affordable
    alternative, most burn the stubble **in situ** — a practice that:

    - 🌫️ Causes **60–80% of Delhi's wintertime PM2.5 spike** (AQI regularly exceeds 500)
    - 🌍 Releases **~17.9 million tonnes of CO₂ equivalent** per season
    - 🏥 Hospitalises thousands with respiratory illness annually
    - 💸 Destroys **~4.5 million tonnes of organic carbon** that could generate energy and income
    """)

    st.markdown("""
    **Why farmers still burn:**
    - Manual stubble removal costs ₹5,000–8,000/acre — unaffordable for most
    - Biomass collection is logistically fragmented
    - Government penalties are poorly enforced and resented
    - No one has offered a *better deal in real time*
    """)

with col_b:
    # AQI data chart
    months = ["Sep", "Oct", "Nov", "Dec", "Jan", "Feb"]
    aqi_normal = [55, 95, 180, 160, 130, 90]
    aqi_burning = [58, 210, 487, 290, 175, 95]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=aqi_normal, name="Without burning",
        line=dict(color="#2ecc71", width=2), fill='tozeroy',
        fillcolor="rgba(46,204,113,0.1)"
    ))
    fig.add_trace(go.Scatter(
        x=months, y=aqi_burning, name="With stubble burning",
        line=dict(color="#ff4e1a", width=3), fill='tozeroy',
        fillcolor="rgba(255,78,26,0.15)"
    ))
    fig.add_hrect(y0=300, y1=550, fillcolor="rgba(255,78,26,0.08)", line_width=0)
    fig.add_annotation(x="Nov", y=510, text="🚨 Hazardous", showarrow=False,
                       font=dict(color="#ff4e1a", size=11))
    fig.update_layout(
        title="Delhi AQI — Seasonal Pattern (PM2.5 µg/m³)",
        paper_bgcolor="#0d1424", plot_bgcolor="#0d1424",
        font_color="#8fa8c8", height=280,
        legend=dict(bgcolor="#111b2e", bordercolor="#1e3352", borderwidth=1),
        margin=dict(l=0, r=0, t=40, b=0),
        yaxis=dict(gridcolor="#1e3352"),
        xaxis=dict(gridcolor="#1e3352"),
    )
    st.plotly_chart(fig, use_container_width=True)

# ── THE INNOVATION ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">The Innovation: Smoke Arbitrage</div>', unsafe_allow_html=True)

st.markdown("""
Agnivāṇī is **not** a surveillance tool or a penalty system. It is an **autonomous Biomass Broker** —
an agent that makes stubble *more valuable unburnt than burnt*, and delivers that offer *proactively*,
*in the farmer's own language*, *at the exact moment it matters*.
""")

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="section-header" style="font-size:1rem">🔁 The Smoke Arbitrage Protocol</div>', unsafe_allow_html=True)
    steps = [
        ("1. Field Intelligence", "AMED API flags 'Recently Harvested' fields at 10–30m resolution, updated every 15 days. Agent identifies fields vulnerable to burning within 48–72 hours."),
        ("2. Risk Computation", "NeuralGCM atmospheric model predicts the smoke trajectory for each field's GPS coordinate based on real-time wind patterns. A Smoke Risk Index (SRI) is computed."),
        ("3. Proactive Outreach", "If SRI trajectory hits a population centre (Delhi, Chandigarh), VoicERA triggers a multilingual Punjabi/Hindi call to the farmer — before any burning starts."),
        ("4. Nocturnal Monitoring", "Sentinel-3 SLSTR F1 fire channels scan at night (5–10 PM evasion window). If a hotspot is detected, the agent triggers a Dynamic Buy-Back call within minutes."),
        ("5. Biomass Brokerage", "Agent books a Bio-CNG plant collection truck, confirms price, and routes payment to the farmer's PM-Kisan DBT account within 24 hours of delivery."),
    ]
    for title, desc in steps:
        st.markdown(f"""
        <div class="flow-step">
            <h4>{title}</h4>
            <p>{desc}</p>
        </div>""", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-header" style="font-size:1rem">📞 The Farmer Conversation</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="quote-box">
        <strong>ਸਤ ਸ੍ਰੀ ਅਕਾਲ, ਵੀਰ ਜੀ।</strong><br>
        "Sat Sri Akal, Veer ji. Our satellite shows your field in <em>[Village]</em> was harvested today.
        If you burn tomorrow, the wind will carry the smoke to your own children's school in Delhi.<br><br>
        However, a Bio-CNG plant nearby is buying stubble at <strong>₹2,400/tonne</strong>.
        Would you like me to book a biomass collection truck for 8:00 AM tomorrow?
        You will receive payment directly to your PM-Kisan account."
    </div>
    <div class="quote-box" style="border-left-color:#f5a623;background:linear-gradient(135deg,#1a1200,#070b07);color:#d4b870">
        <strong>Dynamic Buy-Back (if fire detected):</strong><br>
        "The fire has started, but it is still small. If you douse it now,
        the biomass plant will take the unburnt 90% of your residue at a
        <strong>premium price of ₹3,100/tonne</strong>. Shall I confirm the booking?"
    </div>
    """, unsafe_allow_html=True)

    # Why this works chart
    labels = ['Fear of penalty', 'Social pressure', 'Financial incentive', 'Environmental appeal', 'Real-time offer']
    effectiveness = [22, 35, 78, 41, 85]
    colors = ['#4a6080','#6a80a0','#2ecc71','#8fa8c8','#f5a623']

    fig2 = go.Figure(go.Bar(
        x=effectiveness, y=labels, orientation='h',
        marker_color=colors, text=[f"{v}%" for v in effectiveness],
        textposition='outside', textfont=dict(color='#8fa8c8', size=11)
    ))
    fig2.update_layout(
        title="Farmer Compliance Rate by Intervention Type (est.)",
        paper_bgcolor="#0d1424", plot_bgcolor="#0d1424",
        font_color="#8fa8c8", height=260,
        xaxis=dict(range=[0,100], gridcolor="#1e3352", ticksuffix="%"),
        yaxis=dict(gridcolor="#1e3352"),
        margin=dict(l=0, r=60, t=40, b=0),
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── TECH ARCHITECTURE ──────────────────────────────────────────────────────
st.markdown('<div class="section-header">Technical Architecture — Multi-AI Fusion</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.columns(4)
tech_cards = [
    ("🛰️", "Google AMED API", "Field Intelligence", "10–30m resolution crop monitoring. Tracks Harvest-Ready status, updated every 15 days. Identifies 48–72h burn risk window.", "#f5a623"),
    ("🌙", "Sentinel-3 SLSTR", "Nocturnal Fire Detection", "Sea & Land Surface Temperature Radiometer. F1 & S7 fire channels. Detects night-time evasion burns with higher sensitivity than MODIS.", "#ff4e1a"),
    ("🗣️", "Bhashini + VoicERA", "Multilingual Voice AI", "Open-source Voice AI on India's BHASHINI infrastructure. AWWER-optimised for Punjabi/Haryanvi agricultural terms in noisy fields.", "#2ecc71"),
    ("🌀", "NeuralGCM", "Smoke Trajectory", "Google's hybrid ML + numerical weather prediction model. Computes 72-hour smoke trajectory for each field coordinate using real-time winds.", "#8fa8c8"),
]
for col, (icon, name, role, desc, color) in zip([t1,t2,t3,t4], tech_cards):
    col.markdown(f"""
    <div class="info-box" style="border-top: 3px solid {color}; height: 220px;">
        <div style="font-size:2rem; margin-bottom:8px">{icon}</div>
        <h4 style="color:{color}; font-size:0.85rem">{name}</h4>
        <div style="font-size:0.7rem; color:#4a6080; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px">{role}</div>
        <p style="font-size:0.8rem">{desc}</p>
    </div>""", unsafe_allow_html=True)

# ── IMPACT PROJECTIONS ─────────────────────────────────────────────────────
st.markdown('<div class="section-header">Projected Impact at Scale</div>', unsafe_allow_html=True)

col_i1, col_i2 = st.columns(2)

with col_i1:
    # Diversion curve
    pct = list(range(0, 101, 10))
    co2_saved = [p * 0.179 for p in pct]  # 17.9M tonnes at 100%
    aqi_reduction = [p * 1.52 for p in pct]  # ~152 µg/m³ at 100%
    revenue = [p * 840 for p in pct]  # ₹84,000 crore at 100%

   fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=pct, y=co2_saved, name="CO₂ Avoided (M tonnes)",
                               line=dict(color="#2ecc71", width=2)))
    fig3.add_trace(go.Scatter(x=pct, y=aqi_reduction, name="Delhi AQI Reduction (µg/m³)",
                               line=dict(color="#8fa8c8", width=2), yaxis="y2"))
    fig3.update_layout(
        title="Impact vs. Stubble Diversion Rate",
        paper_bgcolor="#0d1424", plot_bgcolor="#0d1424",
        font_color="#8fa8c8", height=300,
        xaxis=dict(title="Fields Diverted (%)", gridcolor="#1e3352", ticksuffix="%"),
        yaxis=dict(title="CO₂ Avoided (M t)", gridcolor="#1e3352", titlefont=dict(color="#2ecc71")),
        yaxis2=dict(title="AQI Reduction", overlaying="y", side="right", titlefont=dict(color="#8fa8c8")),
        legend=dict(bgcolor="#111b2e", bordercolor="#1e3352", borderwidth=1),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.plotly_chart(fig3, use_container_width=True)

with col_i2:
    # Revenue waterfall
    districts = ["Ludhiana", "Amritsar", "Patiala", "Sangrur", "Moga", "Bathinda", "Ferozepur"]
    area_mha = [3.8, 2.9, 3.1, 2.4, 1.8, 2.2, 1.9]
    revenue_cr = [a * 2.4 * 0.6 * 2400 / 100 for a in area_mha]  # rough estimate

    fig4 = go.Figure(go.Bar(
        x=districts, y=revenue_cr,
        marker=dict(
            color=revenue_cr,
            colorscale=[[0,"#1a3a1a"],[0.5,"#2ecc71"],[1,"#f5a623"]],
        ),
        text=[f"₹{v:.0f}Cr" for v in revenue_cr],
        textposition="outside", textfont=dict(color="#8fa8c8", size=10)
    ))
    fig4.update_layout(
        title="Potential Farmer Revenue by District (@ 60% diversion)",
        paper_bgcolor="#0d1424", plot_bgcolor="#0d1424",
        font_color="#8fa8c8", height=300,
        yaxis=dict(title="Revenue (₹ Crore)", gridcolor="#1e3352"),
        xaxis=dict(gridcolor="#1e3352"),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    st.plotly_chart(fig4, use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="display:flex; justify-content:space-between; color:#4a6080; font-size:0.75rem">
    <span>Agnivāṇī v1.0 · Climate-Tech Solution · Northwestern India Agricultural Belt</span>
    <span>Data sources: ISRO VEDAS · Copernicus SLSTR NRT · Google DeepMind NeuralGCM · MeitY Bhashini</span>
</div>
""", unsafe_allow_html=True)

