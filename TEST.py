import pandas as pd
import yfinance as yf
import numpy as np
import random
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Ratios de Sharpe CAC40", layout="wide")

# --- Données CAC40 ---
ticker_to_name = {
    "SU.PA": "Schneider Electric SE", "TTE.PA": "TotalEnergies SE", "MC.PA": "LVMH",
    "AIR.PA": "Airbus SE", "AI.PA": "Air Liquide SA", "SAF.PA": "Safran SA",
    "SAN.PA": "Sanofi SA", "OR.PA": "L'Oréal SA", "BNP.PA": "BNP Paribas SA",
    "CS.PA": "AXA SA", "EL.PA": "EssilorLuxottica SA", "RMS.PA": "Hermès",
    "DG.PA": "Vinci SA", "SGO.PA": "Saint-Gobain SA", "BN.PA": "Danone SA",
    "ENGI.PA": "Engie SA", "GLE.PA": "Société Générale SA", "LR.PA": "Legrand SA",
    "HO.PA": "Thales SA", "ORA.PA": "Orange SA", "ML.PA": "Michelin SCA",
    "CAP.PA": "Capgemini SE", "PUB.PA": "Publicis Groupe SA", "VIE.PA": "Veolia",
    "DSY.PA": "Dassault Systèmes SE", "STLAP.PA": "Stellantis N.V.",
    "RI.PA": "Pernod Ricard SA", "STMPA.PA": "STMicroelectronics N.V.",
    "ACA.PA": "Crédit Agricole SA", "KER.PA": "Kering SA", "MT.AS": "ArcelorMittal SA",
    "BVI.PA": "Bureau Veritas SA", "URW.PA": "Unibail-Rodamco-Westfield SE",
    "AC.PA": "Accor SA", "RNO.PA": "Renault SA", "ERF.PA": "Eurofins Scientific SE",
    "EN.PA": "Bouygues SA", "EDEN.PA": "Edenred SE", "CA.PA": "Carrefour SA",
    "TEP.PA": "Teleperformance SE"
}

tickers = sorted(list(ticker_to_name.keys()))
name = [ticker_to_name[t] for t in tickers]

data = yf.download(tickers, start="2023-01-01", end="2026-01-01", auto_adjust=True)["Close"]

# --- Calcul du ratio de Sharpe par entreprise ---
rf = 0.02
trading_days = 252
rf_daily = (1 + rf)**(1/trading_days) - 1
RET = data.pct_change().dropna() - rf_daily
RS = RET.mean()/RET.std()*np.sqrt(trading_days)
RS = RS.reset_index()
RS.columns = ["Ticker", "RS"]
RS["name"] = name
RS["size"] = RS["RS"].abs().clip(lower=RS["RS"].abs().quantile(0.05))

fig = px.scatter(
    RS, x="name", y="RS",
    size="size", color="RS",
    color_continuous_scale="Viridis",
    title="Ratio de Sharpe par entreprise (CAC 40)"
)
fig.update_layout(template="plotly_white", xaxis_tickangle=45)

# --- SECTION 1 ---
st.title("📊 Ratio de Sharpe par entreprise")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")  # ← séparation visuelle

# --- Simulation de portefeuilles aléatoires (fig2) ---
RET = data.pct_change().dropna()
weight_cols = name
N = 5000

def CreateWeights(n):
    c2 = random.randint(0, 5)
    c1 = 10 - 2*c2
    L = [0.0]*n
    idx2 = random.sample(range(n), c2)
    for i in idx2:
        L[i] = 0.2
    remaining = list(set(range(n)) - set(idx2))
    idx1 = random.sample(remaining, c1)
    for i in idx1:
        L[i] = 0.1
    return L

Xx = pd.DataFrame(index=range(N), columns=weight_cols + ['rs','ret','vol'], dtype=float)

for n in range(N):
    w = CreateWeights(len(weight_cols))
    Pr = (RET * w).sum(axis=1)
    rf_daily = (1 + rf)**(1/trading_days) - 1
    RETp = Pr - rf_daily
    RS = RETp.mean()/RETp.std(ddof=1)*np.sqrt(trading_days)
    row = w + [RS, RETp.mean()*trading_days, RETp.std(ddof=1)*np.sqrt(trading_days)]
    Xx.loc[n] = row

Xx = Xx.dropna()

fig2 = go.Figure(
    data=[go.Scatter(
        x=Xx['vol'],
        y=Xx['ret'],
        mode='markers',
        marker=dict(
            size=10 + 40*(Xx['rs'] - Xx['rs'].min())/(Xx['rs'].max() - Xx['rs'].min()),
            color=Xx['rs'],
            showscale=True,
            colorbar=dict(title='Sharpe')
        ),
        hovertemplate=(
            "<b>Vol (ann.):</b> %{x:.2%}<br>"
            "<b>Rendement (ann.):</b> %{y:.2%}<br>"
            "<b>Sharpe :</b> %{marker.color:.2f}<extra></extra>"
        )
    )]
)

fig2.update_layout(
    title="Frontière rendement/volatilité (taille ∝ Sharpe)",
    xaxis_title="Volatilité annualisée",
    yaxis_title="Rendement annualisé",
    template="plotly_white",
    width=1200, height=700
)
fig2.update_xaxes(tickformat=".1%")
fig2.update_yaxes(tickformat=".1%")

# --- SECTION 2 ---
st.title("📈 Portefeuilles simulés : rendement vs volatilité")
st.plotly_chart(fig2, use_container_width=True)

