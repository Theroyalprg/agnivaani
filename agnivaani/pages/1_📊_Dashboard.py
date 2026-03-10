import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import requests
import time

st.set_page_config(page_title="Dashboard — Agnivani", page_icon="📊", layout="wide")

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
.section-hdr { font-size:1.2rem; font-weight:800; color:#e8eef8;
    border-left:4px solid #f5a623; padding-left:10px; margin: 1.2rem 0 0.8rem 0; }
.alert-sent {
    background: rgba(46,204,113,0.1); border: 1px solid #2ecc71;
    border-radius: 8px; padding: 12px 16px; margin-bottom: 8px;
    font-size: 0.85rem; color: #2ecc71;
}
.alert-failed {
    background: rgba(255,78,26,0.1); border: 1px solid #ff4e1a;
    border-radius: 8px; padding: 12px 16px; margin-bottom: 8px;
    font-size: 0.85rem; color: #ff4e1a;
}
.n8n-panel {
    background: #0d1a2e; border: 1px solid #2a4a72;
    border-radius: 12px; padding: 18px 20px; margin-bottom: 12px;
}
.n8n-panel h4 { color: #f5a623; margin-bottom: 8px; font-size: 0.95rem; }
.whatsapp-preview {
    background: #0a1a0a; border: 1px solid #1a5c1a;
    border-radius: 10px; padding: 14px 16px; margin-top: 10px;
    font-size: 0.82rem; color: #a8d8a8; line-height: 1.8;
    font-family: monospace;
}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔥 Agnivani")
    st.caption("Nocturnal Biomass-Arbitrage & Smoke-Trajectory Agent")
    st.markdown("---")
    st.markdown("🏠 [Home](/)")
    st.markdown("📊 **Dashboard** — Live Field Monitor")
    st.markdown("🌬️ [Smoke Model](/Smoke_Trajectory)")
    st.markdown("💰 [Economics](/Biomass_Economics)")
    st.markdown("📞 [Voice Calls](/Voice_Call_Log)")
    st.markdown("---")
    st.markdown("**n8n Webhook URL**")
    n8n_webhook = st.text_input(
        "Paste your n8n webhook URL",
        placeholder="https://your-n8n.app.n8n.cloud/webhook/agnivaani-fire-alert",
        help="Copy this from your n8n workflow's Webhook node"
    )
    st.markdown("---")
    st.markdown("**Simulation Controls**")
    auto_refresh = st.toggle("Auto-refresh (10s)", value=False)
    if st.button("Refresh Data"):
        st.rerun()
    st.markdown("---")
    st.caption("Data: Sentinel-3 SLSTR NRT · Google AMED API")

# ── FIELD DATA ────────────────────────────────────────────────────────────────
np.random.seed(int(datetime.now().strftime("%H%M")) % 100)

FIELD_DATA = [
    {"id": "F001", "farmer": "Gurmeet Singh",     "village": "Lohian Khas",  "district": "Moga",            "area_ha": 6.2,  "status": "BURNING",    "harvested_h": 4,  "sri": 87, "lat": 30.82, "lon": 75.17, "phone": "+919876543210"},
    {"id": "F002", "farmer": "Balwinder Kaur",    "village": "Sahnewal",     "district": "Ludhiana",        "area_ha": 4.8,  "status": "HARVESTED",  "harvested_h": 7,  "sri": 72, "lat": 30.90, "lon": 75.83, "phone": "+919876543211"},
    {"id": "F003", "farmer": "Sukhdev Rana",      "village": "Rajpura",      "district": "Patiala",         "area_ha": 3.1,  "status": "HARVESTED",  "harvested_h": 12, "sri": 58, "lat": 30.48, "lon": 76.59, "phone": "+919876543212"},
    {"id": "F004", "farmer": "Harpreet Gill",     "village": "Tarn Taran",   "district": "Amritsar",        "area_ha": 8.4,  "status": "MONITORING", "harvested_h": 18, "sri": 43, "lat": 31.45, "lon": 74.93, "phone": "+919876543213"},
    {"id": "F005", "farmer": "Ranjit Kumar",      "village": "Sirhind",      "district": "Fatehgarh Sahib", "area_ha": 2.7,  "status": "BURNING",    "harvested_h": 6,  "sri": 79, "lat": 30.64, "lon": 76.38, "phone": "+919876543214"},
    {"id": "F006", "farmer": "Daljeet Sandhu",    "village": "Dhuri",        "district": "Sangrur",         "area_ha": 5.1,  "status": "BOOKED",     "harvested_h": 24, "sri": 0,  "lat": 30.05, "lon": 75.87, "phone": "+919876543215"},
    {"id": "F007", "farmer": "Manpreet Dhaliwal", "village": "Rampura Phul", "district": "Bathinda",        "area_ha": 7.3,  "status": "DELIVERED",  "harvested_h": 36, "sri": 0,  "lat": 30.27, "lon": 75.22, "phone": "+919876543216"},
    {"id": "F008", "farmer": "Jagtar Singh",      "village": "Zira",         "district": "Ferozepur",       "area_ha": 4.0,  "status": "HARVESTED",  "harvested_h": 2,  "sri": 61, "lat": 30.96, "lon": 74.99, "phone": "+919876543217"},
    {"id": "F009", "farmer": "Kirpal Brar",       "village": "Phagwara",     "district": "Kapurthala",      "area_ha": 6.6,  "status": "MONITORING", "harvested_h": 20, "sri": 38, "lat": 31.22, "lon": 75.77, "phone": "+919876543218"},
    {"id": "F010", "farmer": "Amarjit Dhillon",   "village": "Barnala",      "district": "Sangrur",         "area_ha": 5.5,  "status": "HARVESTED",  "harvested_h": 10, "sri": 65, "lat": 30.38, "lon": 75.54, "phone": "+919876543219"},
    {"id": "F011", "farmer": "Surjit Kaur",       "village": "Malerkotla",   "district": "Sangrur",         "area_ha": 3.8,  "status": "BOOKED",     "harvested_h": 30, "sri": 0,  "lat": 30.53, "lon": 75.88, "phone": "+919876543220"},
    {"id": "F012", "farmer": "Baljinder Mann",    "village": "Khanna",       "district": "Ludhiana",        "area_ha": 7.1,  "status": "BURNING",    "harvested_h": 5,  "sri": 82, "lat": 30.71, "lon": 76.22, "phone": "+919876543221"},
]

df = pd.DataFrame(FIELD_DATA)

# ── ALERT STATE (session state persists across reruns) ─────────────────────
if "alert_log" not in st.session_state:
    st.session_state.alert_log = []

# ── SEND ALERT FUNCTION ───────────────────────────────────────────────────────
def send_whatsapp_alert(field, webhook_url):
    """Send field data to n8n webhook which triggers WhatsApp message."""
    stubble_tonnes = round(field["area_ha"] * 3.5 * 0.90, 1)
    estimated_revenue = int(stubble_tonnes * 3100 - stubble_tonnes * 420)
    arrival_hrs = round(87 / 14.2, 1)  # rough: distance/wind speed

    payload = {
        "field_id":          field["id"],
        "farmer_name":       field["farmer"],
        "village":           field["village"],
        "district":          field["district"],
        "area_ha":           field["area_ha"],
        "sri":               field["sri"],
        "status":            field["status"],
        "farmer_phone":      field["phone"],
        "estimated_revenue": estimated_revenue,
        "arrival_hrs":       arrival_hrs,
        "timestamp":         datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code in [200, 201]:
            return True, payload, response.json()
        else:
            return False, payload, {"error": f"HTTP {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return False, payload, {"error": "Could not connect to n8n. Check webhook URL."}
    except requests.exceptions.Timeout:
        return False, payload, {"error": "Request timed out after 10s."}
    except Exception as e:
        return False, payload, {"error": str(e)}

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("## 📊 Agnivani — Live Field Dashboard")
st.caption(f"Last updated: {datetime.now().strftime('%d %b %Y, %H:%M:%S IST')}")

# ── KPI ROW ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)
total     = len(df)
burning   = len(df[df.status == "BURNING"])
harvested = len(df[df.status == "HARVESTED"])
booked    = len(df[df.status == "BOOKED"])
delivered = len(df[df.status == "DELIVERED"])
revenue   = sum(r["area_ha"] * 2.5 * 2400 for _, r in df[df.status.isin(["BOOKED","DELIVERED"])].iterrows())

for col, val, lbl, color in zip(
    [c1, c2, c3, c4, c5, c6],
    [total, burning, harvested, booked, delivered, f"Rs.{revenue/100000:.1f}L"],
    ["Fields Monitored", "Active Burns", "Recently Harvested", "Trucks Booked", "Delivered", "Revenue Generated"],
    ["#e8eef8", "#ff4e1a", "#f5a623", "#2ecc71", "#d4a843", "#2ecc71"]
):
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-val" style="color:{color}">{val}</div>
        <div class="metric-lbl">{lbl}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── MAIN LAYOUT ───────────────────────────────────────────────────────────────
map_col, alert_col = st.columns([1.4, 0.6])

with map_col:
    st.markdown('<div class="section-hdr">Sentinel-3 SLSTR Field Map — Punjab / Haryana</div>', unsafe_allow_html=True)

    status_config = {
        "BURNING":    {"color": "#ff4e1a", "size": 22, "symbol": "star"},
        "HARVESTED":  {"color": "#f5a623", "size": 14, "symbol": "circle"},
        "MONITORING": {"color": "#7a8fa8", "size": 12, "symbol": "circle"},
        "BOOKED":     {"color": "#2ecc71", "size": 14, "symbol": "diamond"},
        "DELIVERED":  {"color": "#1a7a42", "size": 14, "symbol": "diamond"},
    }

    fig_map = go.Figure()

    for _, r in df.iterrows():
        angle_rad = np.radians(210)
        dlat = 0.4 * np.cos(angle_rad)
        dlon = 0.4 * np.sin(angle_rad)
        fig_map.add_trace(go.Scattermapbox(
            lat=[r["lat"], r["lat"] + dlat],
            lon=[r["lon"], r["lon"] + dlon],
            mode="lines",
            line=dict(color="rgba(122,143,168,0.2)", width=1),
            showlegend=False, hoverinfo="skip"
        ))

    for status, cfg in status_config.items():
        sub = df[df.status == status]
        if len(sub) == 0:
            continue
        fig_map.add_trace(go.Scattermapbox(
            lat=sub["lat"], lon=sub["lon"],
            mode="markers",
            marker=dict(size=cfg["size"], color=cfg["color"], opacity=0.9),
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

    fig_map.add_trace(go.Scattermapbox(
        lat=[28.6139], lon=[77.2090], mode="markers+text",
        marker=dict(size=16, color="#ff4e1a", symbol="star"),
        text=["Delhi NCR"], textposition="top right",
        textfont=dict(color="#ff4e1a", size=12),
        name="Delhi (AQI Impact Zone)",
        hovertemplate="<b>Delhi NCR</b><br>Primary smoke destination<extra></extra>"
    ))

    fig_map.update_layout(
        mapbox=dict(style="carto-darkmatter", center=dict(lat=30.8, lon=75.8), zoom=6.5),
        paper_bgcolor="#0d1424", font_color="#8fa8c8",
        height=460, margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(bgcolor="#111b2e", bordercolor="#1e3352", borderwidth=1, font=dict(size=11))
    )
    st.plotly_chart(fig_map, use_container_width=True)

# ── N8N ALERT PANEL ───────────────────────────────────────────────────────────
with alert_col:
    st.markdown('<div class="section-hdr">🔔 n8n WhatsApp Alerts</div>', unsafe_allow_html=True)

    # Show critical fields that need alerts
    critical_fields = df[df.status.isin(["BURNING", "HARVESTED"]) & (df.sri >= 60)].sort_values("sri", ascending=False)

    st.markdown(f"""
    <div class="n8n-panel">
        <h4>🛰️ Fields Requiring Immediate Alert</h4>
        <div style="font-size:0.8rem;color:#8fa8c8">
            {len(critical_fields)} fields with SRI >= 60 detected tonight.
            Click a button below to send a WhatsApp alert via n8n.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Individual alert buttons for each critical field
    for _, field in critical_fields.iterrows():
        sri_color = "#ff4e1a" if field["sri"] >= 80 else "#f5a623"
        already_alerted = any(log["field_id"] == field["id"] for log in st.session_state.alert_log)

        with st.container():
            st.markdown(f"""
            <div style="background:#111b2e;border:1px solid {'#ff4e1a' if field['status']=='BURNING' else '#f5a623'}33;
                        border-left:3px solid {sri_color};border-radius:8px;
                        padding:10px 14px;margin-bottom:6px">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="font-size:0.85rem;font-weight:700;color:#e8eef8">
                        {'🔥' if field['status']=='BURNING' else '🌾'} {field['farmer']}
                    </span>
                    <span style="color:{sri_color};font-size:0.75rem;font-weight:800">SRI {field['sri']}</span>
                </div>
                <div style="font-size:0.75rem;color:#8fa8c8;margin-top:2px">
                    {field['village']}, {field['district']} · {field['area_ha']} ha
                </div>
                <div style="font-size:0.72rem;color:#4a6080;margin-top:2px">
                    {field['phone']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            btn_label = "✅ Alert Sent" if already_alerted else f"📲 Send WhatsApp Alert"
            btn_disabled = already_alerted

            if st.button(btn_label, key=f"alert_{field['id']}", disabled=btn_disabled, use_container_width=True):
                if not n8n_webhook or n8n_webhook.strip() == "":
                    st.error("⚠️ Please paste your n8n webhook URL in the sidebar first.")
                else:
                    with st.spinner(f"Sending alert to {field['farmer']}..."):
                        success, payload, response = send_whatsapp_alert(field.to_dict(), n8n_webhook.strip())

                    if success:
                        st.session_state.alert_log.append({
                            "field_id":    field["id"],
                            "farmer":      field["farmer"],
                            "village":     field["village"],
                            "sri":         field["sri"],
                            "time":        datetime.now().strftime("%H:%M:%S"),
                            "revenue_est": payload["estimated_revenue"],
                            "status":      "sent"
                        })
                        st.success(f"✅ WhatsApp alert sent to {field['farmer']} ({field['phone']})")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed: {response.get('error', 'Unknown error')}")

    st.markdown("---")

    # ── SEND ALL CRITICAL AT ONCE ─────────────────────────────────────────────
    unsent_critical = [
        f for _, f in critical_fields.iterrows()
        if not any(log["field_id"] == f["id"] for log in st.session_state.alert_log)
    ]

    if unsent_critical:
        if st.button(f"🚨 Send ALL {len(unsent_critical)} Alerts Now", type="primary", use_container_width=True):
            if not n8n_webhook or n8n_webhook.strip() == "":
                st.error("Please paste your n8n webhook URL in the sidebar first.")
            else:
                progress = st.progress(0, text="Sending alerts...")
                sent_count = 0
                for i, field in enumerate(unsent_critical):
                    with st.spinner(f"Alerting {field['farmer']}..."):
                        success, payload, response = send_whatsapp_alert(field.to_dict(), n8n_webhook.strip())
                        if success:
                            st.session_state.alert_log.append({
                                "field_id":    field["id"],
                                "farmer":      field["farmer"],
                                "village":     field["village"],
                                "sri":         field["sri"],
                                "time":        datetime.now().strftime("%H:%M:%S"),
                                "revenue_est": payload["estimated_revenue"],
                                "status":      "sent"
                            })
                            sent_count += 1
                        progress.progress((i + 1) / len(unsent_critical),
                                          text=f"Sent {i+1}/{len(unsent_critical)}")
                        time.sleep(0.5)  # avoid rate limiting
                st.success(f"✅ {sent_count}/{len(unsent_critical)} alerts sent successfully!")
                st.rerun()

    # ── ALERT LOG ─────────────────────────────────────────────────────────────
    if st.session_state.alert_log:
        st.markdown('<div class="section-hdr" style="font-size:1rem">📋 Tonight\'s Alert Log</div>', unsafe_allow_html=True)
        for log in reversed(st.session_state.alert_log):
            st.markdown(f"""
            <div class="alert-sent">
                ✅ <b>{log['farmer']}</b> · {log['village']} · SRI {log['sri']}<br>
                <span style="font-size:0.75rem;opacity:0.7">
                    Sent at {log['time']} · Est. revenue offer: Rs.{log['revenue_est']:,}
                </span>
            </div>
            """, unsafe_allow_html=True)

        if st.button("🗑️ Clear Alert Log", use_container_width=True):
            st.session_state.alert_log = []
            st.rerun()

    # ── WHATSAPP MESSAGE PREVIEW ──────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-hdr" style="font-size:1rem">📱 Message Preview</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="whatsapp-preview">
        🔥 <b>Agnivaani Alert</b> 🔥<br><br>
        Sat Sri Akal <b>Gurmeet Singh</b> ji.<br><br>
        Our satellite has detected a fire on your field
        in <b>Lohian Khas, Moga</b>.<br><br>
        📊 Smoke Risk Index: <b>87/100</b><br>
        💨 Wind direction: Toward Delhi NCR<br>
        ⏰ Estimated smoke arrival: ~6.1 hours<br><br>
        💰 <b>Special Offer:</b> Douse the fire now and
        we will take the unburnt residue at
        <b>Rs.3,100/tonne</b> — approximately
        <b>Rs.17,360</b> for your field.<br><br>
        🚛 Reply YES to book a collection truck
        for tomorrow 6 AM.<br><br>
        This offer expires in 2 hours.<br><br>
        — Agnivaani Climate Agent
    </div>
    """, unsafe_allow_html=True)

# ── BOTTOM: FIELD STATUS TABLE + TIMESERIES ───────────────────────────────────
st.markdown("---")
left_b, right_b = st.columns([0.6, 1.4])

with left_b:
    st.markdown('<div class="section-hdr">📋 Full Field Log</div>', unsafe_allow_html=True)
    status_colors = {
        "BURNING":    ("#ff4e1a", "rgba(255,78,26,0.12)"),
        "HARVESTED":  ("#f5a623", "rgba(245,166,35,0.1)"),
        "MONITORING": ("#7a8fa8", "rgba(122,143,168,0.08)"),
        "BOOKED":     ("#2ecc71", "rgba(46,204,113,0.1)"),
        "DELIVERED":  ("#1a7a42", "rgba(26,122,66,0.1)"),
    }
    icons = {"BURNING": "🔥", "HARVESTED": "🌾", "MONITORING": "🛰️", "BOOKED": "🚛", "DELIVERED": "✅"}

    for _, row in df.iterrows():
        c, bg = status_colors[row["status"]]
        st.markdown(f"""
        <div style="background:{bg};border:1px solid {c}33;border-radius:8px;
                    padding:9px 12px;margin-bottom:6px;border-left:3px solid {c}">
            <div style="display:flex;justify-content:space-between">
                <span style="font-size:0.82rem;font-weight:700;color:#e8eef8">{row['farmer']}</span>
                <span style="background:{c}22;color:{c};font-size:0.62rem;font-weight:700;
                             padding:2px 7px;border-radius:8px">{icons[row['status']]} {row['status']}</span>
            </div>
            <div style="font-size:0.72rem;color:#8fa8c8;margin-top:2px">
                {row['village']}, {row['district']} · {row['area_ha']} ha · SRI: {row['sri']}
            </div>
        </div>""", unsafe_allow_html=True)

with right_b:
    st.markdown('<div class="section-hdr">📈 Hourly Fire Detections — Last 24 Hours</div>', unsafe_allow_html=True)
    hours_ts = [(datetime.now() - timedelta(hours=23-i)) for i in range(24)]
    np.random.seed(42)
    detections = np.clip(np.random.poisson(3, 24) + np.array([0]*12 + [2,4,6,5,4,3,2,1,1,1,1,0]), 0, 15)
    aqi_vals   = 180 + np.cumsum(np.random.randn(24)*5) + detections * 8

    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(
        x=hours_ts, y=detections, name="Fire Detections",
        line=dict(color="#ff4e1a", width=2.5),
        fill="tozeroy", fillcolor="rgba(255,78,26,0.12)", yaxis="y1"
    ))
    fig_ts.add_trace(go.Scatter(
        x=hours_ts, y=aqi_vals, name="Delhi AQI (est.)",
        line=dict(color="#8fa8c8", width=1.5, dash="dot"), yaxis="y2"
    ))
    fig_ts.add_hline(y=4, line_dash="dash", line_color="#f5a623", opacity=0.5,
                     annotation_text="Alert threshold", annotation_font=dict(color="#f5a623", size=10))
    fig_ts.update_layout(
        paper_bgcolor="#0d1424", plot_bgcolor="#0d1424", font_color="#8fa8c8",
        height=320, margin=dict(l=0, r=0, t=10, b=0),
        yaxis=dict(title="Fire Count", gridcolor="#1e3352"),
        yaxis2=dict(title="AQI", overlaying="y", side="right"),
        legend=dict(bgcolor="#111b2e", bordercolor="#1e3352", borderwidth=1, orientation="h", y=1.02),
        xaxis=dict(gridcolor="#1e3352"),
    )
    st.plotly_chart(fig_ts, use_container_width=True)

if auto_refresh:
    time.sleep(10)
    st.rerun()
