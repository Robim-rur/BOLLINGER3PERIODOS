import streamlit as st
import pandas as pd
import yfinance as yf
import time

st.set_page_config(page_title="Scanner Bollinger B3", layout="wide")

st.title("🔍 Scanner Bollinger (21, 3)")
st.write("Fechamento abaixo da banda inferior (viés de compra)")

# SUA LISTA COMPLETA (ajustada)
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
    df = yf.download(f"{ticker}.SA", period="90d", interval="1d", progress=False)
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

            if df is None or df.empty or len(df) < 25:
                continue

            close = df["Close"]

            if isinstance(close, pd.DataFrame):
                close = close.squeeze()

            close = close.dropna()

            sma = close.rolling(21).mean()
            std = close.rolling(21).std()
            lower = sma - 3 * std

            last_close = close.iloc[-1]
            last_lower = lower.iloc[-1]

            if pd.isna(last_lower):
                continue

            if last_close < last_lower:
                dist = (last_lower - last_close) / last_lower * 100

                results.append({
                    "Ativo": t,
                    "Preço": last_close,
                    "Banda Inferior": last_lower,
                    "Distância (%)": dist
                })

            time.sleep(0.05)  # controle de carga

        except:
            continue

        progress.progress((i + 1) / total)

    status.empty()
    return results


if st.button("🚀 Rodar Scanner Completo"):
    with st.spinner("Analisando mercado..."):
        data = scan()

        st.divider()

        if data:
            df = pd.DataFrame(data)
            df = df.sort_values(by="Distância (%)", ascending=False)

            df["Preço"] = df["Preço"].map(lambda x: f"R$ {x:.2f}")
            df["Banda Inferior"] = df["Banda Inferior"].map(lambda x: f"R$ {x:.2f}")
            df["Distância (%)"] = df["Distância (%)"].map(lambda x: f"{x:.2f}%")

            st.success(f"{len(df)} ativos encontrados")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Nenhum ativo encontrou condição.")
