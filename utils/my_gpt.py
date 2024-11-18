from openai import OpenAI
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import json
import streamlit as st



response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "decision_response",
        "schema": {
            "type": "object",
            "properties": {
                "buy_or_sell": {
                    "type": "string",
                    "enum": ["buy", "sell", "hold"]  # buy,sell,hold 만 허용
                },
                "reason": {
                    "type": "string",
                    "description": "이유를 한 문장으로 출력"  # 한국어로 한줄 출력 명시
                },
            },
            "required": ["buy_or_sell", "reason"],
            "additionalProperties": False
        },
        "strict": True
    }
}

# 4. GPT에게 매수/매도 전략 판단 요청
def get_gpt_decision(current_price, sma_20, sma_50, rsi, bb_upper, bb_lower):
    prompt = f"""
    당신은 주식 매매 전략 전문가입니다. 아래는 특정 주식의 1시간 간격 데이터와 주요 기술적 지표입니다. 이 데이터를 바탕으로, 현재 시점에서의 매수 또는 매도 관망 전략을 추천하세요.
    
    ### 주식 데이터:
    - 현재 시점 주식 가격: {current_price}
    - 20시간 이동평균(SMA_20): {sma_20}
    - 50시간 이동평균(SMA_50): {sma_50}
    - RSI(14시간): {rsi}
    - 볼린저 밴드 상단: {bb_upper}
    - 볼린저 밴드 하단: {bb_lower}

    ### 매수/매도 신호 기준:
    - 20시간 이동평균(SMA_20)이 50시간 이동평균(SMA_50)보다 높다면, 상승 추세로 보고 매수 신호를 고려하세요.
    - 20시간 이동평균(SMA_20)이 50시간 이동평균(SMA_50)보다 낮다면, 하락 추세로 보고 매도 신호를 고려하세요.
    - RSI가 70 이상일 경우 과매수 상태로 보고 매도 신호를 고려하세요.
    - RSI가 30 이하일 경우 과매도 상태로 보고 매수 신호를 고려하세요.
    - 주가가 볼린저 밴드 하단을 이탈한 경우 매수, 상단을 이탈한 경우 매도 신호를 고려하세요.
    
    이 데이터를 바탕으로, 현재 주식을 매수해야 할지, 매도해야 할지, 아니면 관망해야 할지 결정하고 그 이유를 설명해 주세요.
    """
    
    client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": 'user', 'content': prompt}
        ],
        response_format=response_format
    )
    
    result = json.loads(response.choices[0].message.content)
    return result

def get_stock_data(ticker, start_date, end_date, offset=14):
    stock = yf.Ticker(ticker)

    # 한국 시간대로 변환
    korea_tz = pytz.timezone('Asia/Seoul')
    end_date = korea_tz.localize(datetime.strptime(end_date, '%Y-%m-%d'))
    # start_date를 하루 이전으로 설정하고, 시간을 22시로 설정
    start_date = datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=1)
    start_date = start_date.replace(hour=22, minute=0, second=0)
    start_date = korea_tz.localize(start_date)


    # 입력한 날짜로부터 데이터를 가져오기
    df = stock.history(start=start_date-timedelta(offset), end=end_date + timedelta(days=1), interval="1h")
    df.index = df.index.tz_convert('Asia/Seoul')

    # 이동평균 및 기타 지표 계산
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['RSI'] = df['Close'].rolling(window=14).mean()  # 간단한 RSI 구현
    df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = df['Close'].rolling(window=20).mean() + 2 * df['Close'].rolling(window=20).std(), df['Close'].rolling(window=20).mean(), df['Close'].rolling(window=20).mean() - 2 * df['Close'].rolling(window=20).std()

    # 원하는 날짜만 지정
    df = df[df.index >= start_date]

    return df


if __name__ == "__main__":
    # 함수 호출 예시
    ticker = "AAPL"
    start_date = "2024-10-10"
    end_date = "2024-10-15"

    df = get_stock_data(ticker, start_date, end_date)

    # 데이터 출력 확인
    print(df[['Close', 'SMA_20', 'SMA_50', 'RSI']])


    # # 원하는 주식 티커 설정하기
    # ticker = "AAPL"
    # stock = yf.Ticker(ticker=ticker)

    # # 특정 날짜 필터링
    # input_date = input("백테스팅을 시작할 날짜를 입력하세요 (YYYY-MM-DD 형식): ")
    # end_date = datetime.strptime(input_date, '%Y-%m-%d')

    # # 한국 시간대로 변환
    # korea_tz = pytz.timezone('Asia/Seoul')
    # end_date = korea_tz.localize(end_date)
    # end_date = end_date

    # # 입력한 날짜로부터 일주일 전 데이터 가져오기
    # start_date = end_date - timedelta(days=14)
    # df = stock.history(start=start_date, end=end_date + timedelta(days=1), interval="1h")
    # df.index = df.index.tz_convert('Asia/Seoul')


    # # 이동평균 및 기타 지표 계산
    # df['SMA_20'] = df['Close'].rolling(window=20).mean()
    # df['SMA_50'] = df['Close'].rolling(window=50).mean()
    # df['RSI'] = df['Close'].rolling(window=14).mean()  # 간단한 RSI 구현
    # df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = df['Close'].rolling(window=20).mean() + 2 * df['Close'].rolling(window=20).std(), df['Close'].rolling(window=20).mean(), df['Close'].rolling(window=20).mean() - 2 * df['Close'].rolling(window=20).std()

    # # 원하는 날짜만 지정
    # df = df[df.index.date >= end_date.date()]

    # # 백테스팅: 포지션에 따른 가상 거래 시뮬레이션
    # initial_cash = 1000000  # 초기 자본
    # shares = 0  # 보유 주식 수
    # cash = initial_cash
    # df['Portfolio Value'] = initial_cash

    # for i in range(1,len(df)):
    #     # 지표 값 준비
    #     current_price = df['Close'].iloc[i]
    #     sma_20 = df['SMA_20'].iloc[i]
    #     sma_50 = df['SMA_50'].iloc[i]
    #     rsi = df['RSI'].iloc[i]
    #     bb_upper = df['BB_Upper'].iloc[i]
    #     bb_lower = df['BB_Lower'].iloc[i]
        
    #     # GPT로부터 매수/매도 결정 받기
    #     decision = get_gpt_decision(current_price, sma_20, sma_50, rsi, bb_upper, bb_lower)
    #     # GPT의 결정에 따라 매수/매도
    #     if "buy" == decision['buy_or_sell'] and cash > current_price:
    #         shares = cash // current_price  # 살 수 있는 주식 수
    #         cash -= shares * current_price  # 주식을 사고 난 후의 현금
    #         print(f"매수 실행: {df.index[i]}, 주가: {current_price}, 매수 수량: {shares}, 남은 현금: {cash}")
        
    #     elif "sell" == decision['buy_or_sell'] and shares > 0:
    #         cash += shares * current_price  # 주식을 팔아서 현금을 얻음
    #         print(f"매도 실행: {df.index[i]}, 주가: {current_price}, 매도 수량: {shares}, 현금: {cash}")
    #         shares = 0  # 주식을 다 팔았으므로 보유 주식 수는 0
    #     elif "hold" == decision['buy_or_sell']:
    #         print(f"관망 실행: {df.index[i]}, 주가: {current_price}, 현재 수량: {shares}, 현금: {cash}")
    #     print('이유: ',decision['reason'])
        
        
    #     # 현재 포트폴리오 가치 계산 (현금 + 보유 주식 가치)
    #     portfolio_value = cash + shares * current_price
    #     df['Portfolio Value'] = df['Portfolio Value'].astype(float)

    # # 6. 성과 분석 및 출력
    # print(f"최종 포트폴리오 가치: {df['Portfolio Value'].iloc[-1]}")
    # print(df[['Close', 'SMA_20', 'SMA_50', 'RSI', 'Portfolio Value']].tail())
