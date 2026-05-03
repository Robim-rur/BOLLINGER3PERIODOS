import streamlit as st
import pandas as pd
import yfinance as yf
import time

st.set_page_config(page_title="Scanner Bollinger B3", layout="wide")

st.title("🔍 Scanner Bollinger (21, 3)")
st.write("Busca ativos com fechamento abaixo da banda inferior (viés de compra)")

# lista inicial (depois ampliamos)
tickers = [
    "PETR4","VALE3","ITUB4","BOVA11","WEGE3",
    "BBAS3","ABEV3","PRIO3","SUZB3","RENT3"
]

@st.cache_data(ttl=3600)
def get_data(ticker):
    df = yf.download(f"{ticker}.SA", period="90d", interval="1d", progress=False)
    return df

def scan():
    results = []

    progress = st.progress(0)
    status = st.empty()

    for i, t in enumerate(tickers):
        try:
            status.text(f"Processando {t} ({i+1}/{len(tickers)})")

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

            time.sleep(0.1)

        except:
            continue

        progress.progress((i + 1) / len(tickers))

    status.empty()
    return results


if st.button("🚀 Rodar Scanner"):
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
