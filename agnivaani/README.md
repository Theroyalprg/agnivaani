# 🔥 Agnivāṇī — Nocturnal Biomass-Arbitrage & Smoke-Trajectory Agent

A fully working Streamlit dashboard for the Agnivāṇī climate-tech solution targeting stubble burning in the northwestern Indian agricultural belt.

## 🚀 Quick Start (Local)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run Home.py
```

The app opens at **http://localhost:8501**

## 📄 Pages

| Page | Description |
|------|-------------|
| 🏠 Home | Full concept explanation, problem statement, architecture, impact projections |
| 📊 Dashboard | Live field monitor with Sentinel-3 map, SRI scores, burn alerts, timeseries |
| 🌬️ Smoke Trajectory | NeuralGCM wind model, configurable trajectory, AQI forecasting |
| 💰 Biomass Economics | Arbitrage calculator, plant network, PM-Kisan payment flow |
| 📞 Voice Call Log | Bhashini VoicERA call transcripts, funnel analytics, AWWER stats |

## ☁️ Deploy on Streamlit Cloud (Free)

1. Push this folder to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set **Main file path** to `Home.py`
5. Click **Deploy** — live in ~2 minutes

## 🏗️ Project Structure

```
agnivaani/
├── Home.py                          # Main page — concept & overview
├── pages/
│   ├── 1_📊_Dashboard.py           # Field monitoring dashboard
│   ├── 2_🌬️_Smoke_Trajectory.py    # NeuralGCM wind model
│   ├── 3_💰_Biomass_Economics.py   # Arbitrage engine & calculator
│   └── 4_📞_Voice_Call_Log.py      # Bhashini VoicERA log
├── .streamlit/
│   └── config.toml                  # Dark theme config
├── requirements.txt
└── README.md
```

## 🛰️ Data Sources (Production)

| Component | API / Source | Cost |
|-----------|-------------|------|
| Field monitoring | Google AMED API | Free |
| Fire detection | Copernicus Sentinel-3 SLSTR NRT | Free |
| Wind/smoke model | Google NeuralGCM (open-source) | Free |
| Voice AI | MeitY Bhashini + VoicERA | Free |
| Payment | PM-Kisan DBT API | Free |

> **Note:** This prototype uses simulated data. In production, connect each module to its respective API.

