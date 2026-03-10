import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Voice Call Log — Agnivāṇī", page_icon="📞", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Noto+Sans+Gurmukhi:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
.section-hdr { font-size:1.2rem; font-weight:800; color:#e8eef8;
    border-left:4px solid #2ecc71; padding-left:10px; margin:1.2rem 0 0.8rem 0; }
.call-card {
    border-radius:12px; padding:18px 20px; margin-bottom:12px;
    border-left: 4px solid;
}
.call-card.fire     { background:rgba(255,78,26,0.07); border-color:#ff4e1a; }
.call-card.preempt  { background:rgba(245,166,35,0.07); border-color:#f5a623; }
.call-card.accepted { background:rgba(46,204,113,0.07); border-color:#2ecc71; }
.call-card.refused  { background:rgba(122,143,168,0.07); border-color:#7a8fa8; }
.transcript-box {
    background:rgba(7,11,20,0.7); border-radius:8px; padding:14px 16px;
    margin-top:12px; font-size:0.85rem; line-height:1.8; color:#a8c0d8;
    border-left: 3px solid;
}
.punjabi { font-family:'Noto Sans Gurmukhi',sans-serif; color:#2ecc71; font-size:0.95rem; font-weight:600; display:block; margin-bottom:4px; }
.agent-line { color:#f5a623; }
.farmer-line { color:#e8eef8; }
.outcome-pill {
    display:inline-block; padding:3px 12px; border-radius:12px;
    font-size:0.7rem; font-weight:700; letter-spacing:1px; text-transform:uppercase;
}
.stat-mini {
    background:#111b2e; border:1px solid #1e3352; border-radius:8px;
    padding:14px 16px; text-align:center;
}
.stat-mini-val { font-size:1.8rem; font-weight:800; }
.stat-mini-lbl { font-size:0.7rem; color:#8fa8c8; letter-spacing:1px; text-transform:uppercase; margin-top:3px; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔥 Agnivāṇī")
    st.markdown("---")
    st.markdown("🏠 [Home](/)")
    st.markdown("📊 [Dashboard](/Dashboard)")
    st.markdown("🌬️ [Smoke Model](/Smoke_Trajectory)")
    st.markdown("💰 [Economics](/Biomass_Economics)")
    st.markdown("📞 **Voice Calls** — Bhashini Log")
    st.markdown("---")
    st.markdown("**📞 Call Filters**")
    call_type_filter = st.multiselect("Call Type",
        ["Pre-emptive", "Fire Detected (Dynamic)", "Follow-up", "Booking Confirmation"],
        default=["Pre-emptive", "Fire Detected (Dynamic)"])
    outcome_filter = st.multiselect("Outcome",
        ["Accepted", "Refused", "Callback Requested", "No Answer"],
        default=["Accepted", "Refused"])
    st.markdown("---")
    st.markdown("**🎛️ VoicERA Model**")
    st.metric("AWWER Score", "91.3%", "+2.1%")
    st.metric("Punjabi Accuracy", "94.7%", "+0.8%")
    st.metric("Avg Call Duration", "2m 18s", "-12s")
    st.caption("Model: VoicERA · Bhashini AWWER · Agriculture-tuned")

# ── CALL LOG DATA ─────────────────────────────────────────────────────────
CALLS = [
    {
        "id": "C-0041", "type": "fire", "call_type": "Fire Detected (Dynamic)",
        "farmer": "Gurmeet Singh", "village": "Lohian Khas", "district": "Moga",
        "time": "23:33 IST", "duration": "3m 12s", "outcome": "Accepted",
        "outcome_color": "#2ecc71",
        "sri": 87, "offer": "₹3,100/tonne (dynamic buyback)",
        "stubble_saved": "5.6 tonnes (90% of field)",
        "revenue": "₹17,360",
        "punjabi_open": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ, ਵੀਰ ਜੀ। ਸਾਡੇ ਸੈਟੇਲਾਈਟ ਨੇ ਤੁਹਾਡੇ ਖੇਤ ਵਿੱਚ ਅੱਗ ਦੇਖੀ ਹੈ।",
        "transcript": [
            ("AGENT", "Sat Sri Akal, Veer ji. Our Sentinel satellite has detected a small fire on your field in Lohian Khas. The fire has started, but it is still small."),
            ("FARMER", "Haan ji... main hi lagayi si thodi. Kehra satellite?"),
            ("AGENT", "Veer ji, if you douse it now, the Sangrur Bio-CNG plant will still take the unburnt 90% of your residue. Today's special price: ₹3,100 per tonne — that is ₹17,360 for your field, directly to your PM-Kisan account within 24 hours."),
            ("FARMER", "Paani naal bujhana padega? Truck kado aayega?"),
            ("AGENT", "Ji. I am booking the truck right now for 6:00 AM tomorrow. Please douse the fire with the water in your field's irrigation channel. I am sending an SMS with the truck driver's number."),
            ("FARMER", "Theek hai veer ji. Bujhaunga."),
        ]
    },
    {
        "id": "C-0039", "type": "preempt", "call_type": "Pre-emptive",
        "farmer": "Balwinder Kaur", "village": "Sahnewal", "district": "Ludhiana",
        "time": "22:15 IST", "duration": "2m 44s", "outcome": "Callback Requested",
        "outcome_color": "#f5a623",
        "sri": 72, "offer": "₹2,400/tonne (base price)",
        "stubble_saved": "—",
        "revenue": "—",
        "punjabi_open": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ, ਬੀਬੀ ਜੀ। ਤੁਹਾਡਾ ਖੇਤ ਅੱਜ ਵੱਢਿਆ ਗਿਆ ਹੈ।",
        "transcript": [
            ("AGENT", "Sat Sri Akal, Bibi ji. Our satellite shows your 4.8 hectare field in Sahnewal was harvested today. The wind is heading toward Delhi — if burned, smoke will reach the capital in about 8 hours."),
            ("FARMER", "Main jaandi haan. Par mere kol abhi time nahi. Kal gal kariye."),
            ("AGENT", "Ji zaroor. I will call you at 7:00 AM. The Bio-CNG offer at ₹2,400/tonne is valid for 48 hours — that is ₹40,320 for your field."),
            ("FARMER", "Theek hai. Kal subah phone karo."),
        ]
    },
    {
        "id": "C-0038", "type": "fire", "call_type": "Fire Detected (Dynamic)",
        "farmer": "Baljinder Mann", "village": "Khanna", "district": "Ludhiana",
        "time": "23:10 IST", "duration": "1m 55s", "outcome": "Refused",
        "outcome_color": "#7a8fa8",
        "sri": 82, "offer": "₹3,100/tonne (dynamic buyback)",
        "stubble_saved": "—",
        "revenue": "—",
        "punjabi_open": "ਵੀਰ ਜੀ, ਅਸੀਂ ਤੁਹਾਡੇ ਖੇਤ ਵਿੱਚ ਅੱਗ ਦੇਖੀ ਹੈ।",
        "transcript": [
            ("AGENT", "Veer ji, Sentinel satellite has detected fire on your 7.1 ha field in Khanna. The dynamic buyback price is ₹3,100/tonne — over ₹61,000 for your field if you douse it now."),
            ("FARMER", "Yaar, sab laga ditti. Aadha jal gaya. Baaki rakha nahi jaata hune."),
            ("AGENT", "Veer ji, even the remaining 50% is worth ₹30,000. I can send a truck in 2 hours to collect what is left."),
            ("FARMER", "Nahi yaar. Agli bar shayad. Hune nahi hona."),
            ("AGENT", "Ji, samajh aata hai. Next season, please let us call before you decide. I am registering your field for early monitoring next year."),
        ]
    },
    {
        "id": "C-0035", "type": "accepted", "call_type": "Pre-emptive",
        "farmer": "Daljeet Sandhu", "village": "Dhuri", "district": "Sangrur",
        "time": "18:30 IST", "duration": "4m 02s", "outcome": "Accepted",
        "outcome_color": "#2ecc71",
        "sri": 55, "offer": "₹2,400/tonne (base price)",
        "stubble_saved": "12.75 tonnes",
        "revenue": "₹30,600 (net after transport)",
        "punjabi_open": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ ਵੀਰ ਜੀ। ਤੁਹਾਡਾ ਖੇਤ ਕੱਲ੍ਹ ਵੱਢਿਆ ਜਾਵੇਗਾ।",
        "transcript": [
            ("AGENT", "Sat Sri Akal, Veer ji. AMED satellite data shows your 5.1 hectare field in Dhuri will be harvested tomorrow. If residue is burned, wind will carry smoke toward Delhi."),
            ("FARMER", "Haan, combine aa rahi hai kal. Main soch raha si ki agg laga daan. Koi faida nahi lagda truckon da."),
            ("AGENT", "Veer ji, we handle the truck. You just need to say yes. Sangrur Bioenergy is buying at ₹2,400/tonne. Your 12.75 tonnes = ₹30,600 net, credited to your PM-Kisan account by day after tomorrow."),
            ("FARMER", "Sach mein? PM-Kisan account mein?"),
            ("AGENT", "Ji bilkul. Truck aayega subah 6 baje. Driver ka number SMS karanga."),
            ("FARMER", "Theek hai bhai. Kar lo booking."),
            ("AGENT", "Booking confirmed! Truck number: PB-10-AB-3421. Driver: Sukhjinder. Any questions, press 1 to call back."),
        ]
    },
    {
        "id": "C-0031", "type": "accepted", "call_type": "Booking Confirmation",
        "farmer": "Manpreet Dhaliwal", "village": "Rampura Phul", "district": "Bathinda",
        "time": "07:15 IST", "duration": "1m 10s", "outcome": "Accepted",
        "outcome_color": "#2ecc71",
        "sri": 0, "offer": "Delivery confirmation",
        "stubble_saved": "18.25 tonnes delivered",
        "revenue": "₹43,800 (net) — CREDITED",
        "punjabi_open": "ਵੀਰ ਜੀ, ਤੁਹਾਡਾ ਭੁਗਤਾਨ ਭੇਜਿਆ ਜਾ ਰਿਹਾ ਹੈ।",
        "transcript": [
            ("AGENT", "Sat Sri Akal, Veer ji. Your 18.25 tonnes of stubble has been received and weighed at Sangrur Bioenergy. Payment of ₹43,800 is being credited to your PM-Kisan account ending 4782."),
            ("FARMER", "Wah! Itna jaldi! Shukriya bhai."),
            ("AGENT", "Agle saal bhi aapka khet registered hai. Have a good season, Veer ji."),
        ]
    },
]

# ── HEADER ────────────────────────────────────────────────────────────────
st.markdown("## 📞 Bhashini VoicERA — Call Log & Transcripts")
st.caption("Autonomous multilingual voice agent · AWWER-optimised Punjabi · Agriculture-weighted models")

# ── STATS ─────────────────────────────────────────────────────────────────
c1,c2,c3,c4,c5 = st.columns(5)
stats = [
    (len(CALLS), "Total Calls Today", "#e8eef8"),
    (sum(1 for c in CALLS if c["outcome"]=="Accepted"), "Accepted", "#2ecc71"),
    (sum(1 for c in CALLS if c["outcome"]=="Refused"), "Refused", "#7a8fa8"),
    ("91.3%", "Punjabi AWWER", "#f5a623"),
    ("2m 18s", "Avg Duration", "#8fa8c8"),
]
for col, (val, lbl, color) in zip([c1,c2,c3,c4,c5], stats):
    col.markdown(f"""
    <div class="stat-mini">
        <div class="stat-mini-val" style="color:{color}">{val}</div>
        <div class="stat-mini-lbl">{lbl}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── CALLS ─────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1])

with left_col:
    st.markdown('<div class="section-hdr">📋 Call Log</div>', unsafe_allow_html=True)

    selected_call_id = None
    for call in CALLS:
        type_map = {"fire": "🔥 Fire Dynamic", "preempt": "🌾 Pre-emptive", "accepted": "✅ Confirmed", "refused": "🔕 Follow-up"}
        type_color = {"fire": "#ff4e1a", "preempt": "#f5a623", "accepted": "#2ecc71", "refused": "#7a8fa8"}
        tc = type_color[call["type"]]
        expanded = st.expander(
            f"📞 {call['id']} — {call['farmer']} ({call['village']}) · {call['time']}"
        )
        with expanded:
            cols = st.columns(3)
            cols[0].markdown(f"**Type:** <span style='color:{tc}'>{call['call_type']}</span>", unsafe_allow_html=True)
            cols[1].markdown(f"**Duration:** {call['duration']}")
            cols[2].markdown(f"**Outcome:** <span style='color:{call['outcome_color']};font-weight:700'>{call['outcome']}</span>", unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:rgba(7,11,20,0.6);border-radius:8px;padding:10px 14px;
                        margin-top:8px;font-size:0.82rem;color:#8fa8c8;line-height:1.7;
                        border-left:3px solid {tc}">
                <span style="color:#4a6080;font-size:0.7rem">OPENING LINE (Punjabi)</span><br>
                <span class="punjabi">{call['punjabi_open']}</span>
                <b>Offer:</b> {call['offer']}<br>
                <b>SRI at call time:</b> {call['sri']}<br>
                {f"<b>Biomass saved:</b> {call['stubble_saved']}<br><b>Revenue:</b> <span style='color:#2ecc71'>{call['revenue']}</span>" if call['outcome']=='Accepted' else ''}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("**📝 Full Transcript:**")
            for speaker, line in call["transcript"]:
                color = "#f5a623" if speaker == "AGENT" else "#e8eef8"
                label = "🤖 Agent (VoicERA)" if speaker == "AGENT" else "👨‍🌾 Farmer"
                st.markdown(f"""
                <div style="margin-bottom:6px;padding:8px 12px;border-radius:6px;
                            background:{'rgba(245,166,35,0.06)' if speaker=='AGENT' else 'rgba(232,238,248,0.04)'};
                            border-left:2px solid {'#f5a623' if speaker=='AGENT' else '#4a6080'}">
                    <div style="font-size:0.68rem;color:{'#f5a623' if speaker=='AGENT' else '#4a6080'};
                                letter-spacing:1px;text-transform:uppercase;margin-bottom:3px">{label}</div>
                    <div style="font-size:0.85rem;color:{color}">{line}</div>
                </div>""", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="section-hdr">📊 Call Analytics</div>', unsafe_allow_html=True)

    # Acceptance funnel
    funnel_vals = [142, 89, 52, 31, 28]
    funnel_labels = ["Fields Harvested", "AMED Flagged", "Calls Triggered", "Calls Answered", "Accepted Offer"]
    fig_funnel = go.Figure(go.Funnel(
        y=funnel_labels, x=funnel_vals,
        textinfo="value+percent initial",
        marker_color=["#1e3352","#2a4a72","#f5a623","#d4a843","#2ecc71"],
        textfont=dict(color="#e8eef8")
    ))
    fig_funnel.update_layout(
        title="Today's Conversion Funnel",
        paper_bgcolor="#0d1424", plot_bgcolor="#0d1424", font_color="#8fa8c8",
        height=300, margin=dict(l=0,r=0,t=40,b=0)
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

    # Outcome by hour
    hours = list(range(17, 24))
    accepted = [2, 3, 5, 4, 6, 3, 5]
    refused  = [1, 1, 2, 3, 1, 2, 1]
    no_ans   = [3, 2, 1, 2, 2, 1, 2]

    fig_hour = go.Figure()
    fig_hour.add_trace(go.Bar(x=hours, y=accepted, name="Accepted", marker_color="#2ecc71"))
    fig_hour.add_trace(go.Bar(x=hours, y=refused,  name="Refused",  marker_color="#7a8fa8"))
    fig_hour.add_trace(go.Bar(x=hours, y=no_ans,   name="No Answer",marker_color="#1e3352"))
    fig_hour.update_layout(
        barmode="stack", title="Call Outcomes by Hour (IST)",
        paper_bgcolor="#0d1424", plot_bgcolor="#0d1424", font_color="#8fa8c8",
        height=240, margin=dict(l=0,r=0,t=40,b=0),
        yaxis=dict(gridcolor="#1e3352"),
        xaxis=dict(title="Hour (IST)", gridcolor="#1e3352", tickvals=hours, ticktext=[f"{h}:00" for h in hours]),
        legend=dict(bgcolor="#111b2e", bordercolor="#1e3352", borderwidth=1)
    )
    st.plotly_chart(fig_hour, use_container_width=True)

    # Technology breakdown
    st.markdown('<div class="section-hdr" style="font-size:1rem">🗣️ VoicERA Technology</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#111b2e;border:1px solid #1e3352;border-radius:10px;padding:16px 18px">
        <div style="color:#8fa8c8;font-size:0.83rem;line-height:1.9">
        <b style="color:#2ecc71">Bhashini Infrastructure:</b> India's national AI translation platform by MeitY. Powers real-time ASR, TTS, and NMT across 22 scheduled languages.<br>
        <b style="color:#2ecc71">VoicERA Stack:</b> Open-source Voice AI. Whisper-based ASR → LLM reasoning → Indic TTS. Optimised for low-bandwidth rural networks (2G/3G compatible).<br>
        <b style="color:#2ecc71">AWWER Metric:</b> Agriculture Weighted Word Error Rate. Custom vocabulary for crop terms, village names, and market prices in Punjabi/Haryanvi dialects.<br>
        <b style="color:#2ecc71">Noisy field robustness:</b> SNR tested at 15dB+ ambient noise (tractor, combine harvester). Model fine-tuned on 2,400+ hours of field audio.
        </div>
    </div>
    """, unsafe_allow_html=True)

