import requests
import streamlit as st

# Discord url
LEADERBOARD_URL=st.secrets['LEADERBOARD_URL']
REALTIME_URL=st.secrets['REALTIME_URL']

# 디스코드 봇 토큰
TOKEN = st.secrets['TOKEN']
# 리더보드 채널 ID
CHANNEL_ID = st.secrets['CHANNEL_ID']


def get_discord_messages(token=TOKEN, channel_id=CHANNEL_ID, limit=100):

    url = f'https://discord.com/api/v10/channels/{channel_id}/messages'
    headers = {'Authorization': f'Bot {token}'}
    params = {'limit': limit}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Failed to retrieve messages: {response.status_code} - {response.text}"

def parse_message(message):
    lines = message['content'].split('\n')
    data = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip()
    return data

# Function to send message to Discord via webhook
def send_discord_message(message, url):
    data = {
        "content": message,  # The message you want to send
        "username": "실시간 주식마법사",  # Customize the name for the message sender (optional)
    }

    response = requests.post(url, json=data)
    
    if response.status_code == 204:
        st.success("성공적으로 발송되었습니다.")
    else:
        st.error(f"매시지 발송에 실패했습니다.. Status code: {response.status_code}")