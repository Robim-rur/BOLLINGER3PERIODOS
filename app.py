import streamlit as st
import pandas as pd
import yfinance as yf
import time

st.set_page_config(page_title="Scanner Bollinger PRO FLEX", layout="wide")

st.title("📊 Scanner Bollinger PRO FLEX (21, 2.5)")
st.write("Reversão com tendência (EMA 69) + filtros inteligentes")

# LISTA AMPLIADA (líquidos + seus ativos)
tickers = [
    "PETR4","VALE3","ITUB4","BBDC4","BBAS3","ABEV3","WEGE3","RENT3","PRIO3","SUZB3",
    "RADL3","LREN3","RAIL3","EGIE3","HYPE3","EQTL3","ENEV3","MULT3","TOTS3","TIMS3",
    "UGPA3","VIVT3","SBSP3","TAEE11","CPFE3","CMIG4","ELET3","ELET6","CSAN3","CYRE3",
    "MRVE3","EZTC3","DIRR3","JHSF3","GGBR4","GOAU4","USIM5","KLBN11","SUZB3","BRFS3",
    "JBSS3","MRFG3","SMTO3","SLCE3","HAPV3","FLRY3","ODPV3","RDOR3","QUAL3","HYPE3",
    "B3SA3","CASH3","MGLU3","VIIA3","BHIA3","LWSA3","POSI3","INTB3","MOVI3","CVCB3",
    "YDUQ3","COGN3","ARZZ3","ASAI3","PCAR3","CRFB3","NTCO3","VIVA3","AMER3",
    "BOVA11","IVVB11","SMAL11","DIVO11","GOLD11",
    "KNRI11","HGLG11","XPLG11","VISC11","XPML11","MXRF11","IRDM11","CPTS11","HGRU11",
    "GGRC11","TRXF11","ALZR11","VGIA11","AUVP11",
    "AAPL34","MSFT34","GOGL34","AMZO34","TSLA34","META34","NVDC34","NFLX34","MELI34"
]

@st.cache_data(ttl=3600)
def get_data(ticker):
    return yf.download(f"{ticker}.SA", period="120d", interval="1d", progress=False)

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

            # ===== INDICADORES =====
            sma21 = close.rolling(21).mean()
            std21 = close.rolling(21).std()
            lower = sma21 - 2.5 * std21
            ema69 = close.ewm(span=69).mean()

            last_close = close.iloc[-1]
            last_lower = lower.iloc[-1]
            last_ema69 = ema69.iloc[-1]

            if pd.isna(last_lower) or pd.isna(last_ema69):
                continue

            # ===== FILTRO DE TENDÊNCIA FLEXÍVEL =====
            if last_close < last_ema69 * 0.98:
                continue

            # ===== ENTRADA FLEXÍVEL =====
            if last_close <= last_lower * 1.01:

                dist_banda = (last_lower - last_close) / last_lower * 100
                dist_ema = (last_close - last_ema69) / last_ema69 * 100

                # score simples de qualidade
                score = dist_banda + abs(dist_ema)

                results.append({
                    "Ativo": t,
                    "Preço": last_close,
                    "Banda Inferior": last_lower,
                    "EMA 69": last_ema69,
                    "Distância Banda (%)": dist_banda,
                    "Distância EMA (%)": dist_ema,
                    "Score": score
                })

            time.sleep(0.05)

        except:
            continue

        progress.progress((i + 1) / total)

    status.empty()
    return results


if st.button("🚀 Rodar Scanner PRO FLEX"):
    with st.spinner("Analisando mercado..."):
        data = scan()

        st.divider()

        if data:
            df = pd.DataFrame(data)

            # ranking por score
            df = df.sort_values(by="Score", ascending=False)

            df["Preço"] = df["Preço"].map(lambda x: f"R$ {x:.2f}")
            df["Banda Inferior"] = df["Banda Inferior"].map(lambda x: f"R$ {x:.2f}")
            df["EMA 69"] = df["EMA 69"].map(lambda x: f"R$ {x:.2f}")
            df["Distância Banda (%)"] = df["Distância Banda (%)"].map(lambda x: f"{x:.2f}%")
            df["Distância EMA (%)"] = df["Distância EMA (%)"].map(lambda x: f"{x:.2f}%")
            df["Score"] = df["Score"].map(lambda x: f"{x:.2f}")

            st.success(f"{len(df)} ativos com sinal qualificado")
            st.dataframe(df, use_container_width=True)

        else:
            st.warning("Nenhum sinal encontrado — mercado forte ou sem extremos.")
