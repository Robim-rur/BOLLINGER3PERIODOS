import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Scanner Bollinger", layout="wide")

st.title("🔍 Scanner Bollinger (21, 3)")
st.write("Clique no botão para rodar o scan.")

# lista pequena para garantir funcionamento
tickers = ["PETR4","VALE3","ITUB4","BOVA11","WEGE3"]

@st.cache_data(ttl=3600)
def get_data(ticker):
    df = yf.download(f"{ticker}.SA", period="90d", interval="1d", progress=False)
    return df

def run_scan():
    results = []

    for t in tickers:
        try:
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
                    "Banda": last_lower,
                    "Distância (%)": dist
                })

        except:
            continue

    return results

if st.button("🚀 Rodar Scanner"):
    with st.spinner("Analisando..."):
        data = run_scan()

        if data:
            df = pd.DataFrame(data)
            st.dataframe(df)
        else:
            st.warning("Nenhum ativo encontrado.")
