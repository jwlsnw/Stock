import datetime
import FinanceDataReader as fdr
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="나만의 주식 대시보드", layout="wide")

st.title("📈 주식 & 시장 지표 한눈에 보기")
st.caption("주요 지수, 환율, 개별 종목의 차트를 한곳에서 확인하세요.")

# --- 사이드바 설정 ---
st.sidebar.header("⚙️ 설정")
today = datetime.date.today()
start_date = st.sidebar.date_input(
    "조회 시작일", today - datetime.timedelta(days=365)
)

# 종목 코드 입력 (기본값: 삼성전자 005930)
stock_code = st.sidebar.text_input(
    "종목 코드 입력 (6자리)", value="005930"
)


# 데이터 불러오기 함수
@st.cache_data
def get_stock_data(code, start):
    return fdr.DataReader(code, start)


# --- 1. 주요 시장 지표 (지수 & 환율) ---
st.subheader("🌐 주요 시장 지표 (지수 및 환율)")

col1, col2, col3, col4 = st.columns(4)

try:
    # 데이터 수집 (코스피, 코스닥, 원/달러 환율, S&P500)
    kospi = fdr.DataReader("KS11", today - datetime.timedelta(days=7))
    kosdaq = fdr.DataReader("KQ11", today - datetime.timedelta(days=7))
    usdkrw = fdr.DataReader("USD/KRW", today - datetime.timedelta(days=7))
    sp500 = fdr.DataReader("US500", today - datetime.timedelta(days=7))

    # 지표 카드 표시
    with col1:
        st.metric(
            "KOSPI",
            f"{kospi['Close'].iloc[-1]:,.2f}",
            f"{kospi['Close'].iloc[-1] - kospi['Close'].iloc[-2]:,.2f}",
        )
    with col2:
        st.metric(
            "KOSDAQ",
            f"{kosdaq['Close'].iloc[-1]:,.2f}",
            f"{kosdaq['Close'].iloc[-1] - kosdaq['Close'].iloc[-2]:,.2f}",
        )
    with col3:
        st.metric(
            "원/달러 환율",
            f"{usdkrw['Close'].iloc[-1]:,.2f}원",
            f"{usdkrw['Close'].iloc[-1] - usdkrw['Close'].iloc[-2]:,.2f}",
        )
    with col4:
        st.metric(
            "S&P 500",
            f"{sp500['Close'].iloc[-1]:,.2f}",
            f"{sp500['Close'].iloc[-1] - sp500['Close'].iloc[-2]:,.2f}",
        )
except Exception as e:
    st.warning("시장 지표 데이터를 불러오는 중 오류가 발생했습니다.")

st.divider()

# --- 2. 개별 종목 주가 캔들차트 ---
st.subheader(f"📊 개별 종목 차트 분석 (종목코드: {stock_code})")

try:
    df = get_stock_data(stock_code, start_date)

    if not df.empty:
        # Plotly를 활용한 캔들스틱 차트 생성
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

        # 최근 주가 데이터 표 출력
        st.write("📋 **최근 5일 거래 데이터**")
        st.dataframe(df.tail(5).sort_index(ascending=False))
    else:
        st.error("해당 종목의 데이터가 없습니다. 종목 코드를 확인해 주세요.")

except Exception as e:
    st.error(
        "종목 데이터를 가져오지 못했습니다. 종목 코드(예: 삼성전자 005930)를 올바르게 입력했는지 확인해 주세요."
    )
