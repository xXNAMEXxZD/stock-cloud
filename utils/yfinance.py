import yfinance as yf

# yfinance에서 사용할 주식종목
stocks = {
    "삼성전자": "005930.KS",
    "애플": "AAPL",
    "마이크로소프트": "MSFT",
    "구글": "GOOGL",
    "아마존": "AMZN",
    "테슬라": "TSLA",
    "네이버": "035420.KS",
    "카카오": "035720.KS",
    "엔비디아": "NVDA",
    "인텔": "INTC",
    "워너 브로스": "WBD",
    "마스터 카드": "MA",
    "3M": "MMM",
    "디즈니": "DIS",
    "라이엇": "RIOT",
    "암드": "AMD",
    "메르세데스 벤츠": "MBG.DE",
    "BMW": "BMW.DE",
    "알리바바": "BABA",
}



# @st.cache_data()
def get_stock_data(ticker, chart_type, period):
    data = yf.Ticker(ticker)

    interval = "1d"
    if chart_type == "D":
        interval = "1d"
    elif chart_type == "W":
        interval = "1wk"
    elif chart_type == "M":
        interval = "1mo"
    elif chart_type == "Q":
        interval = "3mo"
    # elif chart_type == "Y":
    #     interval = "12mo"
    stock = data.history(interval=interval, period=period)

    return stock


# @st.cache_data()
def get_ma_data(ticker, period, timeframe="D"):
    """
    주어진 주식 종목의 지정된 기간 동안 이동평균 데이터를 계산하여 반환합니다.

    Args:
        stock_ticker (str): 주식의 티커(종목 코드).
        start_date (str): 조회 시작 날짜 (형식: 'YYYY-MM-DD').
        end_date (str): 조회 종료 날짜 (형식: 'YYYY-MM-DD').

    Returns:
        pd.DataFrame: 주식의 가격 정보와 함께 이동평균(SMA 20일, SMA 50일) 및 볼린저 밴드 데이터가 포함된 데이터프레임.
        
    설명:
        - 주식 데이터를 가져와 20일 및 50일 단순 이동평균(SMA)을 계산.
        - 볼린저 밴드 상한과 하한을 계산하여 반환.
    """
    data = yf.Ticker(ticker)
    data = data.history(period)

    # 각 기간에 대한 이동평균 계산
    ma_periods = [5, 20, 60, 120]
    for ma_period in ma_periods:
        data[f"MA{ma_period}"] = data["Close"].rolling(window=ma_period).mean()

    # 지정된 timeframe으로 리샘플링
    if timeframe == "D":  # 일봉
        resampled_data = data
    elif timeframe == "W":  # 주봉
        resampled_data = data.resample("W").last()
    elif timeframe == "M":  # 월봉
        resampled_data = data.resample("M").last()
    elif timeframe == "Q":  # 분기봉
        resampled_data = data.resample("Q").last()
    else:
        raise ValueError("timeframe must be 'D', 'W', 'M', or 'Q'")
    # 필요한 열만 선택 (종가와 이동평균들)
    columns_to_keep = ["Close"] + [f"MA{ma_period}" for ma_period in ma_periods]
    ma_data = resampled_data[columns_to_keep]

    return ma_data



def get_realtime_price(ticker):
    data = yf.Ticker(ticker)
    today = data.history(interval="1m", period="1d")
    if not today.empty:
        latest_price = today["Close"].iloc[-1]
        return latest_price
    else:
        return None

def get_realtime_stock_data(ticker):
    data = yf.Ticker(ticker)
    today = data.history(interval="1m", period="1d")
    if not today.empty:
        return today.iloc[-1]
    else:
        return None