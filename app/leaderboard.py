import streamlit as st
import pandas as pd
import plotly.express as px
from utils.discord import get_discord_messages, parse_message

def create_leaderboard(messages):
    parsed_data = [parse_message(msg) for msg in messages if '수익률' in msg['content']]
    df = pd.DataFrame(parsed_data)
    df['수익률'] = df['수익률'].str.rstrip('%').astype('float')
    df['초기자금'] = df['초기자금'].str.replace('_', '').astype(int)
    df['수익금'] = df['수익금'].str.replace(',', '').astype(int)
    df = df.sort_values('수익률', ascending=False).reset_index(drop=True)
    df.index += 1  # Rank starting from 1
    return df

st.title("📈 리더보드")

if st.button('리더보드 업데이트'):
    st.rerun()

with st.spinner('메시지를 불러오는 중...'):
    messages = get_discord_messages()
    if isinstance(messages, list):
        df = create_leaderboard(messages)
        
        # Main content
        st.header("🏆 순위표")
        
        # 데이터프레임 표시
        st.dataframe(
            df,
            column_config={
                "index": "순위",
                "유저": "유저",
                "주식": "주식",
                "수익률": st.column_config.NumberColumn(
                    "수익률",
                    format="%.2f%%"
                ),
                "초기자금": st.column_config.NumberColumn(
                    "초기자금",
                    format="₩%d"
                ),
                "수익금": st.column_config.NumberColumn(
                    "수익금",
                    format="₩%d"
                ),
                "기간": "거래 기간"
            },
            hide_index=True,
        )
        
        st.header("📊 수익률 분포")
        fig = px.bar(df, x='유저', y='수익률', text='수익률', hover_data=['주식', '초기자금', '수익금'])
        fig.update_traces(textposition='outside')
        fig.update_layout(xaxis_title="유저", yaxis_title="수익률 (%)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(messages)