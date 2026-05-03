import streamlit as st
import pandas as pd
import yfinance as yf
import time

st.set_page_config(page_title="Scanner PRO EDGE", layout="wide")

st.title("📊 Scanner PRO EDGE (Bollinger + Probabilidade)")
st.write("Setup: BB 21/2.5 + EMA69 + Gain 8% / Loss 5%")

# ================= LISTA COMPLETA =================
tickers = [
"RRRP3","ALOS3","ALPA4","ABEV3","ARZZ3","ASAI3","AZUL4",
"B3SA3","BBAS3","BBDC3","BBDC4","BBSE3","BEEF3","BPAC11",
"BRAP4","BRFS3","BRKM5","CCRO3","CMIG4","CMIN3","COGN3",
"CPFE3","CPLE6","CRFB3","CSAN3","CSNA3","CYRE3","DXCO3",
"EGIE3","ELET3","ELET6","EMBR3","ENEV3","ENGI11","EQTL3",
"EZTC3","FLRY3","GGBR4","GOAU4","GOLL4","HAPV3","HYPE3",
"ITSA4","ITUB4","JBSS3","KLBN11","LREN3","LWSA3","MGLU3",
"MRFG3","MRVE3","MULT3","NTCO3","PETR3","PETR4","PRIO3",
"RADL3","RAIL3","RAIZ4","RENT3","RECV3","SANB11","SBSP3",
"SLCE3","SMTO3","SUZB3","TAEE11","TIMS3","TTEN3","TOTS3",
"TRPL4","UGPA3","USIM5","VALE3","VIVT3","VIVA3","WEGE3",
"YDUQ3","AURE3","BHIA3","CASH3","CVCB3","DIRR3","ENAT3",
"GMAT3","IFCM3","INTB3","JHSF3","KEPL3","MOVI3","ORVR3",
"PETZ3","PLAS3","POMO4","POSI3","RANI3","RAPT4","STBP3",
"TEND3","TUPY3","BRSR6","CXSE3",

"AAPL34","AMZO34","GOGL34","MSFT34","TSLA34","META34",
"NFLX34","NVDC34","MELI34","BABA34","DISB34","PYPL34",
"JNJB34","PGCO34","KOCH34","VISA34","WMTB34","NIKE34",
"ADBE34","AVGO34","CSCO34","COST34","CVSH34","GECO34",
"GSGI34","HDCO34","INTC34","JPMC34","MAEL34","MCDP34",
"MDLZ34","MRCK34","ORCL34","PEP334","PFIZ34","PMIC34",
"QCOM34","SBUX34","TGTB34","TMOS34","TXN34","UNHH34",
"UPSB34","VZUA34","ABTT34","AMGN34","AXPB34","BAOO34",
"C2OL34","HONB34","BICE34","BERK34","GOGL35",

"BOVA11","IVVB11","SMAL11","HASH11","GOLD11","DIVO11",
"NDIV11","SPUB11",

"GARE11","HGLG11","XPLG11","VILG11","BRCO11","BTLG11",
"XPML11","VISC11","HSML11","MALL11","KNRI11","JSRE11",
"PVBI11","HGRE11","MXRF11","KNCR11","KNIP11","CPTS11",
"IRDM11","TGAR11","TRXF11","HGRU11","ALZR11","XPCA11",
"VGIA11","RBRR11","KNSC11","CACR11","HABT11","DEVA11",
"HGCR11","MCCI11","RECR11","VRTA11","BCFF11","HFOF11",
"XPSF11","RBRP11","RBRF11","URIT11","RZTR11","RURA11",
"VGIR11","CVBI11","UTLL11","GGRC11","HERT11","AUVP11","IEEX11"
]

# ================= LOTE =================
batch_size = 25
batch_index = st.selectbox("Escolha o lote", range(0, len(tickers)//batch_size + 1))
tickers_batch = tickers[batch_index*batch_size:(batch_index+1)*batch_size]

# ================= DATA =================
@st.cache_data(ttl=3600)
def get_data(ticker):
    return yf.download(f"{ticker}.SA", period="2y", interval="1d", progress=False)

# ================= PROBABILIDADE =================
def calc_prob(df):
    wins, losses = 0, 0

    close = df["Close"].dropna()
    sma = close.rolling(21).mean()
    std = close.rolling(21).std()
    lower = sma - 2.5 * std
    ema = close.ewm(span=69).mean()

    for i in range(80, len(close)-20):

        price = close.iloc[i]

        if pd.isna(lower.iloc[i]) or pd.isna(ema.iloc[i]):
            continue

        if price >= ema.iloc[i]*0.98 and price <= lower.iloc[i]*1.01:

            entry = price
            gain = entry * 1.08
            stop = entry * 0.95

            future = close.iloc[i+1:i+20]

            for f in future:
                if f >= gain:
                    wins += 1
                    break
                elif f <= stop:
                    losses += 1
                    break

    total = wins + losses
    if total == 0:
        return None

    return wins / total * 100

# ================= SCAN =================
def scan():
    results = []

    progress = st.progress(0)
    status = st.empty()

    for i, t in enumerate(tickers_batch):
        try:
            status.text(f"{t} ({i+1}/{len(tickers_batch)})")

            df = get_data(t)

            if df is None or len(df) < 100:
                continue

            close = df["Close"].dropna()

            sma = close.rolling(21).mean()
            std = close.rolling(21).std()
            lower = sma - 2.5 * std
            ema = close.ewm(span=69).mean()

            last = close.iloc[-1]

            if last >= ema.iloc[-1]*0.98 and last <= lower.iloc[-1]*1.01:

                prob = calc_prob(df)

                if prob is None:
                    continue

                results.append({
                    "Ativo": t,
                    "Preço": last,
                    "Prob Gain (%)": prob
                })

            time.sleep(0.05)

        except:
            continue

        progress.progress((i+1)/len(tickers_batch))

    status.empty()
    return results

# ================= EXECUÇÃO =================
if st.button("🚀 Rodar Scanner"):
    with st.spinner("Processando..."):

        data = scan()

        if data:
            df = pd.DataFrame(data)
            df = df.sort_values(by="Prob Gain (%)", ascending=False)

            df["Preço"] = df["Preço"].map(lambda x: f"R$ {x:.2f}")
            df["Prob Gain (%)"] = df["Prob Gain (%)"].map(lambda x: f"{x:.1f}%")

            st.success("Ranking por probabilidade:")
            st.dataframe(df, use_container_width=True)

        else:
            st.warning("Nenhum ativo com sinal neste lote.")
