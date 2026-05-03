import streamlit as st
import pandas as pd
import yfinance as yf
import time

st.set_page_config(page_title="Scanner Bollinger PRO", layout="wide")

st.title("📊 Scanner Bollinger PRO (21, 2.5)")
st.write("Sinais de reversão com filtro de tendência (EMA 69)")

# Lista de ativos (sua base)
tickers = [
    "RRRP3","ALOS3","ALPA4","ABEV3","ARZZ3","ASAI3","AZUL4","B3SA3","BBAS3","BBDC4","BBSE3","BPAC11",
    "BRFS3","CCRO3","CMIG4","CPFE3","CPLE6","CSAN3","CSNA3","CYRE3","DXCO3","EGIE3","ELET3","ELET6",
    "EMBR3","ENEV3","EQTL3","EZTC3","FLRY3","GGBR4","GOAU4","HAPV3","HYPE3","ITSA4","ITUB4","JBSS3",
    "KLBN11","LREN3","MGLU3","MRFG3","MRVE3","MULT3","NTCO3","PETR4","PRIO3","RADL3","RAIL3","RENT3",
    "SANB11","SBSP3","SLCE3","SUZB3","TAEE11","TIMS3","TOTS3","UGPA3","USIM5","VALE3","VIVT3","WEGE3",
    "YDUQ3","AAPL34","AMZO34","GOGL34","MSFT34","TSLA34","META34","NFLX34","NVDC34","MELI34",
    "BOVA11","IVVB11","SMAL11","GOLD11","DIVO11","GARE11","HGLG11","XPLG11","VILG11","XPML11","VISC11",
    "KNRI11","MXRF11","KNCR11","CPTS11","IRDM11","TRXF11","HGRU11","ALZR11","VGIA11","GGRC11","AUVP11"
]

@st.cache_data(ttl=3600)
def get_data(ticker):
    df = yf.download(f"{ticker}.SA", period="120d", interval="1d", progress=False)
    return df

def scan():
    results = []

    progress = st.progress(0)
    status = st.empty()

    total = len(tickers)

    for i, t in enumerate(tickers):
        try:
            status.text(f"Processando {t} ({i+1}/{total})")

            df = get_data(t)

            if df is None or df.empty or len(df) < 80:
                continue

            close = df["Close"]

            if isinstance(close, pd.DataFrame):
                close = close.squeeze()

            close = close.dropna()

            # === INDICADORES ===
            sma21 = close.rolling(21).mean()
            std21 = close.rolling(21).std()

            lower = sma21 - 2.5 * std21
            ema69 = close.ewm(span=69).mean()

            last_close = close.iloc[-1]
            last_lower = lower.iloc[-1]
            last_ema69 = ema69.iloc[-1]

            if pd.isna(last_lower) or pd.isna(last_ema69):
                continue

            # === FILTROS ===

            # 1. Tendência (seu padrão)
            if last_close < last_ema69:
                continue

            # 2. Sinal Bollinger
            if last_close < last_lower:

                # Qualidade do sinal (quanto mais longe da banda, melhor)
                dist = (last_lower - last_close) / last_lower * 100

                results.append({
                    "Ativo": t,
                    "Preço": last_close,
                    "Banda Inferior": last_lower,
                    "EMA 69": last_ema69,
                    "Distância (%)": dist
                })

            time.sleep(0.05)

        except:
            continue

        progress.progress((i + 1) / total)

    status.empty()
    return results


if st.button("🚀 Rodar Scanner PRO"):
    with st.spinner("Analisando mercado..."):
        data = scan()

        st.divider()

        if data:
            df = pd.DataFrame(data)

            # Ranking: maior distância = melhor sinal
            df = df.sort_values(by="Distância (%)", ascending=False)

            df["Preço"] = df["Preço"].map(lambda x: f"R$ {x:.2f}")
            df["Banda Inferior"] = df["Banda Inferior"].map(lambda x: f"R$ {x:.2f}")
            df["EMA 69"] = df["EMA 69"].map(lambda x: f"R$ {x:.2f}")
            df["Distância (%)"] = df["Distância (%)"].map(lambda x: f"{x:.2f}%")

            st.success(f"{len(df)} ativos com sinal QUALIFICADO")
            st.dataframe(df, use_container_width=True)

        else:
            st.warning("Nenhum sinal qualificado encontrado.")
