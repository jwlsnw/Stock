import datetime
import FinanceDataReader as fdr
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="나만의 주식 대시보드", layout="wide")

st.title("📈 주식 & 시장 지표 한눈에 보기")
st.caption("주요 지수 및 개별 종목의 차트를 한곳에서 확인하세요.")

# --- 사이드바 설정 ---
st.sidebar.header("⚙️ 설정")
today = datetime.date.today()
start_date = st.sidebar.date_input(
    "조회 시작일", today - datetime.timedelta(days=365)
)

stock_code = st.sidebar.text_input(
    "종목 코드 입력 (6자리)", value="005930"
)


# 데이터 불러오기 함수
@st.cache_data(ttl=3600)
def get_data(symbol, start):
    try:
        return fdr.DataReader(symbol, start)
    except Exception:
        return pd.DataFrame()


# --- 1. 주요 시장 지표 ---
st.subheader("🌐 주요 시장 지표 (지수)")

col1, col2 = st.columns(2)

kospi = get_data("KS11", today - datetime.timedelta(days=14))
kosdaq = get_data("KQ11", today - datetime.timedelta(days=14))

with col1:
    if not kospi.empty and len(kospi) >= 2:
        diff = kospi["Close"].iloc[-1] - kospi["Close"].iloc[-2]
        st.metric(
            "KOSPI",
            f"{kospi['Close'].iloc[-1]:,.2f}",
            f"{diff:,.2f}",
        )
    else:
        st.info("KOSPI 데이터를 불러오는 중...")

with col2:
    if not kosdaq.empty and len(kosdaq) >= 2:
        diff = kosdaq["Close"].iloc[-1] - kosdaq["Close"].iloc[-2]
        st.metric(
            "KOSDAQ",
            f"{kosdaq['Close'].iloc[-1]:,.2f}",
            f"{diff:,.2f}",
        )
    else:
        st.info("KOSDAQ 데이터를 불러오는 중...")

st.divider()

# --- 2. 개별 종목 차트 ---
st.subheader(f"📊 개별 종목 차트 분석 (종목코드: {stock_code})")

df = get_data(stock_code, start_date)

if not df.empty:
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="주가",
            )
        ]
    )
    fig.update_layout(
        title=f"종목 코드 {stock_code} 주가 추이",
        xaxis_title="날짜",
        yaxis_title="주가 (원)",
        xaxis_rangeslider_visible=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.write("📋 **최근 5일 거래 데이터**")
    st.dataframe(df.tail(5).sort_index(ascending=False))
else:
    st.error("종목 데이터를 가져오지 못했습니다. 종목 코드를 확인해 주세요.")
