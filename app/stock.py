import streamlit as st
import plotly.graph_objs as go
from utils.yfinance import stocks, get_ma_data,get_realtime_price,get_realtime_stock_data,get_stock_data
from utils.discord import send_discord_message,REALTIME_URL


@st.fragment(run_every='60s')
def realtime_metrics():
    metrics = st.empty()
    with metrics:
        
        res = get_realtime_stock_data(stocks[selected_stock])
        current_price=res['Close']
        price_change=res['Close'] - res['Open']
        percentage_change=price_change/res['Open'] * 100
        st.metric(label=selected_stock, value=f'{res['Close']}', delta=f"{percentage_change:.2f} %")

        if alarm:
            send_discord_message(f'{selected_stock}: {res['Close']} {percentage_change:.2f}%', url=REALTIME_URL)

def generate_signals(data):
    # 골든 크로스 / 데드 크로스 (5일 vs 20일)
    data["golden_cross_5_20"] = (data["MA5"] > data["MA20"]) & (
        data["MA5"].shift(1) <= data["MA20"].shift(1)
    )
    data["dead_cross_5_20"] = (data["MA5"] < data["MA20"]) & (
        data["MA5"].shift(1) >= data["MA20"].shift(1)
    )

    data["buy_signal"] = data["golden_cross_5_20"]
    data["sell_signal"] = data["dead_cross_5_20"] 
    

    return data



st.title('실시간 주식차트')


selected_stock = st.selectbox(
    "종목을 선택하세요",
    list(stocks.keys()),
)

chart_type_container, period_container = st.columns(2)

with chart_type_container:
    chart_type_options = {
        "일봉": "D",
        "주봉": "W",
        "월봉": "M",
        "분기": "Q",
        # "년": "Y",
    }
    selected_chart_type = st.selectbox(
        "차트 유형을 선택하세요",
        list(chart_type_options.keys()),
    )
    chart_type = chart_type_options[selected_chart_type]

with period_container:
    period_options = {
        "1년": "1y",
        "1일": "1d",
        "5일": "5d",
        "1개월": "1mo",
        "3개월": "3mo",
        "6개월": "6mo",
        "2년": "2y",
        "5년": "5y",
        "10년": "10y",
        "연초부터": "ytd",
        "최대": "max",
    }
    selected_period = st.selectbox(
        "기간을 선택하세요",
        list(period_options.keys()),
    )
    period = period_options[selected_period]


with st.expander('차트 옵션'):
    options = st.columns([2,1])

    with options[0]:
        st.write('이동평균선')
        ma_cols = st.columns(4)
    with options[1]:
        st.write('실시간 알람')
        alarm = st.checkbox("실시간 알람보내기")

with ma_cols[0]:
    show_ma5 = st.checkbox("5일", value=True)
with ma_cols[1]:
    show_ma20 = st.checkbox("20일", value=True)
with ma_cols[2]:
    show_ma60 = st.checkbox("60일", value=True)
with ma_cols[3]:
    show_ma120 = st.checkbox("120일", value=True)

@st.fragment(run_every='60s')
def stock_layout():
    if selected_stock and selected_chart_type and selected_period:

        data = get_stock_data(stocks[selected_stock], chart_type, period)
        ma_data = get_ma_data(stocks[selected_stock], period, chart_type)
        current_price = get_realtime_price(stocks[selected_stock])
        data.loc[data.index[-1],"Close"] = current_price

        if not data.empty:

            realtime_metrics()


            graph = st.empty()
            s1 = st.container()

            fig = go.Figure()

            # 매매 신호 생성
            signal_data = generate_signals(ma_data)

            # 현재 상태에 대한 매매 신호 표시
            with s1:
                st.subheader("현재 매매 신호")
                current_signal = signal_data.iloc[-1]
                if current_signal["buy_signal"]:
                    st.success("매수 신호")
                elif current_signal["sell_signal"]:
                    st.error("매도 신호")
                else:
                    st.info("중립")

            with graph:
                # 차트에 매수/매도 신호 표시
                buy_signals = signal_data[signal_data["buy_signal"]]
                sell_signals = signal_data[signal_data["sell_signal"]]

                fig.add_trace(
                    go.Scatter(
                        x=buy_signals.index,
                        y=buy_signals["Close"],
                        mode="markers",
                        marker=dict(symbol="triangle-up", size=20, color="red"),
                        name="매수 신호",
                    )
                )

                fig.add_trace(
                    go.Scatter(
                        x=sell_signals.index,
                        y=sell_signals["Close"],
                        mode="markers",
                        marker=dict(symbol="triangle-down", size=20, color="blue"),
                        name="매도 신호",
                    )
                )

                # 캔들스틱 차트 추가
                fig.add_trace(
                    go.Candlestick(
                        x=data.index,
                        open=data["Open"],
                        high=data["High"],
                        low=data["Low"],
                        close=data["Close"],
                        name="주가",
                    )
                )

                # 이동평균선 추가
                if show_ma5:
                    fig.add_trace(
                        go.Scatter(
                            x=ma_data.index,
                            y=ma_data["MA5"],
                            name="5일 이동평균",
                            line=dict(color="green"),
                        )
                    )
                if show_ma20:
                    fig.add_trace(
                        go.Scatter(
                            x=ma_data.index,
                            y=ma_data["MA20"],
                            name="20일 이동평균",
                            line=dict(color="red"),
                        )
                    )
                if show_ma60:
                    fig.add_trace(
                        go.Scatter(
                            x=ma_data.index,
                            y=ma_data["MA60"],
                            name="60일 이동평균",
                            line=dict(color="orange"),
                        )
                    )
                if show_ma120:
                    fig.add_trace(
                        go.Scatter(
                            x=ma_data.index,
                            y=ma_data["MA120"],
                            name="120일 이동평균",
                            line=dict(color="purple"),
                        )
                    )

                fig.update_layout(
                    title=f"{selected_stock} 주식 차트",
                    yaxis_title="주가",
                    xaxis_title="날짜",
                    xaxis_rangeslider_visible=False,
                )

                # Streamlit에 차트 표시
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("종목, 타입, 기간 모두 선택해 주세요.")


stock_layout()