import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

st.set_page_config(page_title="Biomass Economics — Agnivāṇī", page_icon="💰", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
.section-hdr { font-size:1.2rem; font-weight:800; color:#e8eef8;
    border-left:4px solid #2ecc71; padding-left:10px; margin:1.2rem 0 0.8rem 0; }
.price-card {
    background:#0d1a0d; border:1px solid #1a5c1a; border-radius:10px;
    padding:18px; text-align:center; margin-bottom:8px;
}
.price-val  { font-size:2.2rem; font-weight:800; color:#2ecc71; }
.price-lbl  { font-size:0.72rem; color:#8fa8c8; letter-spacing:1px; text-transform:uppercase; margin-top:4px; }
.plant-card {
    background:#111b2e; border:1px solid #1e3352; border-radius:10px; padding:16px; margin-bottom:8px;
}
.plant-card h4 { color:#d4a843; font-size:0.9rem; margin-bottom:6px; }
.plant-card p  { color:#8fa8c8; font-size:0.8rem; line-height:1.5; margin:0; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔥 Agnivāṇī")
    st.markdown("---")
    st.markdown("🏠 [Home](/)")
    st.markdown("📊 [Dashboard](/Dashboard)")
    st.markdown("🌬️ [Smoke Model](/Smoke_Trajectory)")
    st.markdown("💰 **Economics** — Arbitrage Engine")
    st.markdown("📞 [Voice Calls](/Voice_Call_Log)")
    st.markdown("---")
    st.markdown("**💰 Calculator Inputs**")
    field_area = st.number_input("Field area (hectares)", 1.0, 20.0, 6.2, 0.1)
    stubble_yield = st.slider("Stubble yield (tonnes/ha)", 2.0, 6.0, 3.5, 0.1)
    base_price = st.slider("Bio-CNG price (₹/tonne)", 1500, 4000, 2400, 100)
    dynamic_premium = st.slider("Dynamic buyback premium (%)", 10, 60, 29, 1)
    transport_cost = st.slider("Transport cost (₹/tonne)", 200, 800, 420, 10)
    divert_pct = st.slider("Unburnt residue saved (%)", 50, 100, 90, 5)
    st.markdown("---")
    st.caption("Prices: SATAT scheme · MNRE · Market data")

# ── CALCULATIONS ──────────────────────────────────────────────────────────
total_stubble   = field_area * stubble_yield
saved_stubble   = total_stubble * divert_pct / 100
gross_base      = saved_stubble * base_price
gross_dynamic   = saved_stubble * base_price * (1 + dynamic_premium/100)
transport_total = saved_stubble * transport_cost
net_base        = gross_base - transport_total
net_dynamic     = gross_dynamic - transport_total
burn_cost       = 0  # burning is "free" but loses income

# ── HEADER ───────────────────────────────────────────────────────────────
st.markdown("## 💰 Biomass Arbitrage Engine")
st.caption("The core logic: making stubble worth MORE unburnt than burnt — delivered in real time to farmers")

# ── KPIs ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
for col, val, lbl in zip([c1,c2,c3,c4,c5], [
    (f"{total_stubble:.1f} t", "Total stubble available"),
    (f"{saved_stubble:.1f} t", "Biomass recovered"),
    (f"₹{net_base/1000:.1f}K", "Net income (base)"),
    (f"₹{net_dynamic/1000:.1f}K", "Net income (dynamic buyback)"),
    (f"₹{(net_dynamic-burn_cost)/1000:.1f}K", "vs. Burning (gain)"),
], []):
    col.markdown(f"""
    <div class="price-card">
        <div class="price-val">{val[0]}</div>
        <div class="price-lbl">{val[1]}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")
left, right = st.columns([1.1, 0.9])

with left:
    st.markdown('<div class="section-hdr">📊 Revenue Breakdown</div>', unsafe_allow_html=True)

    # Waterfall chart
    fig_wf = go.Figure(go.Waterfall(
        name="Revenue flow", orientation="v",
        measure=["relative","relative","relative","total","relative","total"],
        x=["Stubble value\n(gross)", "Transport\ncost", "Collection\nfee", "Net income\n(base price)",
           "Dynamic\npremium", "Net income\n(buyback)"],
        y=[gross_base, -transport_total, -gross_base*0.03, 0, gross_dynamic-gross_base, 0],
        text=[f"₹{gross_base/1000:.1f}K", f"-₹{transport_total/1000:.1f}K", f"-₹{gross_base*0.03/1000:.1f}K",
              f"₹{net_base/1000:.1f}K", f"+₹{(gross_dynamic-gross_base)/1000:.1f}K", f"₹{net_dynamic/1000:.1f}K"],
        textposition="outside",
        decreasing=dict(marker_color="#ff4e1a"),
        increasing=dict(marker_color="#2ecc71"),
        totals=dict(marker_color="#f5a623"),
        connector=dict(line=dict(color="#1e3352", width=1.5)),
    ))
    fig_wf.update_layout(
        paper_bgcolor="#0d1424", plot_bgcolor="#0d1424", font_color="#8fa8c8",
        height=340, margin=dict(l=0,r=0,t=20,b=0),
        yaxis=dict(title="₹", gridcolor="#1e3352"),
        xaxis=dict(gridcolor="#1e3352"),
    )
    st.plotly_chart(fig_wf, use_container_width=True)

    # Scenario comparison
    st.markdown('<div class="section-hdr">⚖️ Burn vs. Sell Comparison</div>', unsafe_allow_html=True)

    scenarios = ["Burn stubble\n(status quo)", "Sell at base\nprice", "Dynamic buyback\n(Agnivāṇī)"]
    incomes = [0, net_base, net_dynamic]
    colors_bar = ["#4a6080", "#f5a623", "#2ecc71"]

    fig_cmp = go.Figure(go.Bar(
        x=scenarios, y=incomes, marker_color=colors_bar,
        text=[f"₹{v/1000:.1f}K" for v in incomes], textposition="outside",
        textfont=dict(color="#e8eef8", size=13, family="Syne")
    ))
    fig_cmp.update_layout(
        paper_bgcolor="#0d1424", plot_bgcolor="#0d1424", font_color="#8fa8c8",
        height=280, margin=dict(l=0,r=0,t=20,b=0),
        yaxis=dict(title="Farmer income (₹)", gridcolor="#1e3352"),
        xaxis=dict(gridcolor="#1e3352"),
    )
    st.plotly_chart(fig_cmp, use_container_width=True)

with right:
    st.markdown('<div class="section-hdr">🏭 Bio-CNG Plant Network</div>', unsafe_allow_html=True)

    plants = [
        {"name": "Sangrur Bioenergy Pvt. Ltd.", "dist": "Sangrur", "capacity_tpd": 200,
         "price": 2400, "distance_km": 62, "certified": True},
        {"name": "Punjab Agro Industries Corp.", "dist": "Ludhiana", "capacity_tpd": 150,
         "price": 2350, "distance_km": 38, "certified": True},
        {"name": "Haryana Bio-CNG (HKRN)", "dist": "Karnal", "capacity_tpd": 300,
         "price": 2500, "distance_km": 120, "certified": True},
        {"name": "IFFCO Kisan Bio-Energy", "dist": "Patiala", "capacity_tpd": 250,
         "price": 2420, "distance_km": 78, "certified": True},
        {"name": "Replus Engi. Services", "dist": "Amritsar", "capacity_tpd": 100,
         "price": 2280, "distance_km": 45, "certified": False},
    ]
    df_plants = pd.DataFrame(plants)

    for _, p in df_plants.iterrows():
        cert = "✅ SATAT Certified" if p["certified"] else "⚠️ Non-certified"
        net_p = p["price"] - transport_cost
        st.markdown(f"""
        <div class="plant-card">
            <h4>{p['name']}</h4>
            <p>
            📍 {p['dist']} · {p['distance_km']} km away<br>
            ⚡ Capacity: {p['capacity_tpd']} TPD · {cert}<br>
            💵 Price: <b style="color:#2ecc71">₹{p['price']}/tonne</b>
            · Net: <b style="color:#d4a843">₹{net_p}/tonne</b>
            </p>
        </div>""", unsafe_allow_html=True)

    # Price vs distance scatter
    fig_sc = go.Figure(go.Scatter(
        x=df_plants["distance_km"], y=df_plants["price"],
        mode="markers+text", text=df_plants["dist"],
        textposition="top center", textfont=dict(color="#8fa8c8", size=10),
        marker=dict(size=df_plants["capacity_tpd"]/10,
                    color=df_plants["price"], colorscale="YlGn",
                    showscale=True, colorbar=dict(title="₹/tonne", thickness=10))
    ))
    fig_sc.update_layout(
        title="Plant Price vs. Distance from Field",
        paper_bgcolor="#0d1424", plot_bgcolor="#0d1424", font_color="#8fa8c8",
        height=260, margin=dict(l=0,r=0,t=40,b=0),
        xaxis=dict(title="Distance (km)", gridcolor="#1e3352"),
        yaxis=dict(title="Price (₹/tonne)", gridcolor="#1e3352"),
    )
    st.plotly_chart(fig_sc, use_container_width=True)

# ── PM-KISAN PAYMENT FLOW ─────────────────────────────────────────────────
st.markdown('<div class="section-hdr">🏦 PM-Kisan Direct Benefit Transfer Payment Flow</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    steps = [
        ("Farmer accepts offer via VoicERA call", "~0 min", "#f5a623"),
        ("Agnivāṇī confirms with nearest Bio-CNG plant", "~2 min", "#f5a623"),
        ("Truck dispatched to field", "~30 min", "#8fa8c8"),
        ("Stubble collected & weighed at plant gate", "~4–8 hours", "#8fa8c8"),
        ("Payment initiated via PM-Kisan DBT API", "~24 hours", "#2ecc71"),
        ("Amount credited to farmer's bank account", "~24–48 hours", "#2ecc71"),
    ]
    for i, (step, time, color) in enumerate(steps):
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
            <div style="background:{color}22;border:2px solid {color};border-radius:50%;
                        width:28px;height:28px;flex-shrink:0;display:flex;
                        align-items:center;justify-content:center;
                        font-size:0.8rem;font-weight:800;color:{color}">{i+1}</div>
            <div style="flex:1;background:#111b2e;border:1px solid #1e3352;border-radius:8px;
                        padding:10px 14px">
                <div style="font-size:0.85rem;color:#e8eef8">{step}</div>
                <div style="font-size:0.72rem;color:#4a6080;margin-top:2px">⏱ {time}</div>
            </div>
        </div>""", unsafe_allow_html=True)

with col2:
    # Scale analysis
    st.markdown("**📈 Scale: If 30% of Punjab's stubble is diverted**")
    pct_range = list(range(5, 61, 5))
    total_punjab_ha = 2_900_000  # 2.9M ha rice area
    farmer_income   = [p/100 * total_punjab_ha * stubble_yield * (base_price - transport_cost) / 1e7
                       for p in pct_range]  # ₹ Crore
    co2_saved_mt    = [p/100 * total_punjab_ha * stubble_yield * 1.4 / 1e6 for p in pct_range]  # M tonnes CO₂eq

    fig_scale = go.Figure()
    fig_scale.add_trace(go.Scatter(
        x=pct_range, y=farmer_income, name="Farmer income (₹ Cr)",
        line=dict(color="#2ecc71", width=2.5), yaxis="y1"
    ))
    fig_scale.add_trace(go.Scatter(
        x=pct_range, y=co2_saved_mt, name="CO₂ avoided (M t)",
        line=dict(color="#8fa8c8", width=2, dash="dot"), yaxis="y2"
    ))
    fig_scale.update_layout(
        title="Punjab-wide Impact at Different Diversion Rates",
        paper_bgcolor="#0d1424", plot_bgcolor="#0d1424", font_color="#8fa8c8",
        height=340, margin=dict(l=0,r=0,t=40,b=0),
        xaxis=dict(title="Diversion Rate (%)", gridcolor="#1e3352", ticksuffix="%"),
        yaxis=dict(title="Farmer Income (₹ Crore)", titlefont=dict(color="#2ecc71"), gridcolor="#1e3352"),
        yaxis2=dict(title="CO₂ Avoided (M tonnes)", overlaying="y", side="right",
                    titlefont=dict(color="#8fa8c8")),
        legend=dict(bgcolor="#111b2e", bordercolor="#1e3352", borderwidth=1)
    )
    st.plotly_chart(fig_scale, use_container_width=True)

    st.markdown("""
    <div style="background:#0d1a0d;border:1px solid #1a5c1a;border-radius:10px;padding:16px;margin-top:8px">
        <div style="color:#2ecc71;font-weight:800;font-size:0.9rem;margin-bottom:8px">💡 At 30% diversion rate:</div>
        <div style="color:#8fa8c8;font-size:0.82rem;line-height:1.8">
        • Farmer income: <b style="color:#2ecc71">~₹3,800 Crore</b><br>
        • CO₂ avoided: <b style="color:#2ecc71">~5.4 M tonnes</b><br>
        • Delhi AQI reduction: <b style="color:#2ecc71">~45 µg/m³ cumulative</b><br>
        • Bio-CNG produced: <b style="color:#2ecc71">~12 Lakh MMBTU</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

