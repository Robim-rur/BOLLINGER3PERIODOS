import streamlit as st
import pandas as pd
import yfinance as yf
import time

st.set_page_config(page_title="Scanner Bollinger B3", layout="wide")

st.title("🔍 Scanner Bollinger (21, 3)")
st.markdown("Setup: fechamento abaixo da banda inferior")

# Lista de ativos (pode expandir depois)
tickers = [
    "PETR4","VALE3","ITUB4","BOVA11","WEGE3",
    "BBAS3","ABEV3","PRIO3","SUZB3","RENT3"
]

def fetch():
    results = []
    progress = st.progress(0)
    status = st.empty()

    for i, t in enumerate(tickers):
        try:
            status.text(f"Processando {t} ({i+1}/{len(tickers)})")

            df = yf.download(f"{t}.SA", period="90d", interval="1d", progress=False)

            if df is None or df.empty or len(df) < 25:
                continue

            close = df["Close"]

            if isinstance(close, pd.DataFrame):
                close = close.squeeze()

            close = close.dropna()

            if len(close) < 25:
                continue

            # Bollinger manual
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
                    "Preço": round(last_close, 2),
                    "Banda": round(last_lower, 2),
                    "Distancia": dist
                })

            # evita bloqueio do Yahoo
            time.sleep(0.1)

        except Exception as e:
            continue

        progress.progress((i + 1) / len(tickers))

    status.empty()
    return results


if st.button("🚀 Rodar Scanner"):
    with st.spinner("Analisando..."):
        data = fetch()

        st.divider()

        if data:
            df = pd.DataFrame(data)
            df = df.sort_values(by="Distancia", ascending=False)

            df["Preço"] = df["Preço"].map(lambda x: f"R$ {x:.2f}")
            df["Banda"] = df["Banda"].map(lambda x: f"R$ {x:.2f}")
            df["Distancia"] = df["Distancia"].map(lambda x: f"{x:.2f}%")

            st.success(f"{len(df)} ativos encontrados")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Nenhum ativo encontrou condição.")

st.sidebar.info("Rodar após o fechamento do mercado.")
