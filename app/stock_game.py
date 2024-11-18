import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from utils.my_gpt import get_gpt_decision, get_stock_data
from utils.discord import send_discord_message
from utils.yfinance import stocks

# Discord url
LEADERBOARD_URL=st.secrets['LEADERBOARD_URL']


@st.fragment()
def submit_button():
    # 채널에 제출하기 버튼
    if st.button('리더보드에 제출하기'):
        수익금 = portfolio_value - initial_cash
        message = f"유저:{st.session_state['email']}\n주식:{ticker}\n수익률:{returns[-1]:.2f}%\n초기자금:{initial_cash:_}\n수익금:{수익금:,.0f}\n기간:{start_date.strftime('%Y/%m/%d')}~{end_date.strftime('%Y/%m/%d')}"
        send_discord_message(message, url=LEADERBOARD_URL)


# Streamlit 페이지
st.title('주식 백테스팅 시뮬레이션 게임')

# 사용자 입력 받기
selected_stock = st.selectbox(
    "종목을 선택하세요",
    list(stocks.keys()),
)

ticker = stocks[selected_stock]

cols = st.columns(3)

with cols[0]:
    start_date = st.date_input('시작 날짜를 선택하세요', datetime(2024, 10, 10))
with cols[1]:
    end_date = st.date_input('끝 날짜를 선택하세요', datetime(2024, 10, 10))
with cols[2]:
    initial_cash = st.number_input(label='초기자금', min_value=0, value=1000000)

# 시뮬레이션 실행 버튼
if st.button('시뮬레이션 실행',use_container_width=True, type='primary'):
    df = get_stock_data(ticker, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    print(df['SMA_20']) # 주식 데이터를 갖고 와 그 데이터를 기반으로 계산된 기술 분석 지표(SMA_20)를 출력함.
    # 초기 자본 설정
    cash = initial_cash
    shares = 0
    portfolio_values = []
    returns = []

    table = st.empty()  # 거래 내역을 표시할 빈 공간
    graph = st.empty()  # 그래프를 표시할 빈 공간

    # 매수/매도 기록을 저장할 리스트 초기화
    trade_records = []

    # 시뮬레이션 실행
    for i in range(1, len(df)):   # 보통 이동평균 및 지표들이 첫 번째 인덱스에서는 계산이 완료되지 않기 때문에 인덱스 두 번째 부터 시작 - 마지막까지 for문을 돌림
        current_price = df['Close'].iloc[i]
        sma_20 = df['SMA_20'].iloc[i]   # 20일 단순 이동평균(SMA_20) 값을 가져와 sma_20 변수에 할당함
        sma_50 = df['SMA_50'].iloc[i]   # 50일 단순 이동평균(SMA_50) 값을 가져와 sma_50 변수에 할당함
        rsi = df['RSI'].iloc[i]     # 이 값은 자산의 과매수 혹은 과매도 상태를 나타냄
        bb_upper = df['BB_Upper'].iloc[i]   # 불린저 밴드의 상단 값을 가져옴
        bb_lower = df['BB_Lower'].iloc[i]   # 불린저 밴드의 하단 값을 가져옴
        #이 지표는 가격의 변동성과 과매수/과매도 여부를 판단하는데 사용됨
        
        # GPT로부터 매수/매도 결정 받기
        decision = get_gpt_decision(current_price, sma_20, sma_50, rsi, bb_upper, bb_lower)
        decision_type = decision.get("buy_or_sell")     # decision 딕셔너리에서 buy_or_sell 이라는 key값에 해당하는 value값을 가져옴
        reason = decision.get("reason")     # decision 딕셔너리에서 reason 이라는 key값에 해당하는 value값을 가져옴
        # 
        # 매수, 매도, 관망 결정
        if decision_type == "buy" and cash >= current_price:    # decision_type이 "buy"이고 cash(보유현금)이 current_price와 같거나 더 클 때 실행되는 코드
            shares = cash // current_price      # 현재 보유 현금으로 살 수 있는 최대 주식 수를 shares 변수에 할당함/ //연산자는 정수 나눗셈에서 소수점을 버림
            cash -= shares * current_price      # 주식을 구매한 후 사용한 금액만큼 cash에서 차감함, shares * current_price는 매수에 사용된 금액임
            trade_records.append([df.index[i], current_price, 'Buy', shares, cash, reason])     # 매수 거래 기록을 trade_records 리스트에 추가함
        elif decision_type == "sell" and shares > 0:    # decision_type이 "sell"이고 shares가 0보다 클 때 실행됨
            cash += shares * current_price      # 현재 보유한 주식을 전량 매도하여 얻은 금액을 cash에 추가함, shares * current_price는 매도로 얻은 총 금액임
            trade_records.append([df.index[i], current_price, 'Sell', shares, cash, reason])    # 매도 거래 기록을 trade_records 리스트에 추가함
            shares = 0      # 매도 후 shares값을 0으로 변환환
        else:
            trade_records.append([df.index[i], current_price, 'Hold', shares, cash, reason])    # 위의 조건에 맞지 않을 때 실행됨, 매수도 매도도 하지 않고 보유(‘Hold’) 상태로 남음

        # 거래 기록을 DataFrame으로 변환하여 표로 출력
        trade_df = pd.DataFrame(trade_records, columns=['시간', '주가', '결정', '수량', '남은 현금', '이유'])
        with table:
            st.dataframe(trade_df)

        # 포트폴리오 가치 계산 및 수익률 계산
        portfolio_value = cash + shares * current_price
        portfolio_values.append(portfolio_value)

        # 수익률 계산 (포트폴리오 가치에서 초기 자본을 뺀 값의 비율)
        current_return = (portfolio_value - initial_cash) / initial_cash * 100
        returns.append(current_return)

        # Plotly 그래프 업데이트
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index[:len(returns)], y=returns, mode='lines', name='포트폴리오 수익률'))
        fig.update_layout(title='포트폴리오 수익률 추이', xaxis_title='시간', yaxis_title='수익률(%)')

        with graph:
            st.plotly_chart(fig, use_container_width=True)

    # 시뮬레이션 결과 출력
    st.write(f"최종 포트폴리오 가치: {portfolio_value:.2f} 원")
    st.write(f"최종 수익률: {returns[-1]:.2f}%")

    submit_button()