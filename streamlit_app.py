import streamlit as st
import yaml
from yaml.loader import SafeLoader

# Loading config file
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

if'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None


#로그인 페이지
login_page = st.Page('app/account.py', title='로그인', icon=":material/login:")
#로그아웃 페이지
logout_page = st.Page('app/account.py', title='로그아웃', icon=":material/logout:")
# 세팅 페이지
settings_page = st.Page("app/settings.py", title="세팅",  icon=":material/settings:")


# 주식페이지
stock_page = st.Page("app/stock.py", title='주식', icon=':material/monitoring:', default=st.session_state['authentication_status'])
# 게임페이지
game_page = st.Page('app/stock_game.py', title='게임', icon=':material/videogame_asset:')
# 리더보드페이지
leaderboard_page = st.Page('app/leaderboard.py', title='리더보드', icon=':material/trophy:')



page_dict = {}

if st.session_state['authentication_status'] == True:
    page_dict["내 계정"] = [settings_page, logout_page]
    page_dict["주식마법사"] = [stock_page, game_page, leaderboard_page]
else:
    page_dict['시작'] = [login_page,leaderboard_page]


# if len(page_dict) > 0:
pg = st.navigation(page_dict, position="sidebar")

pg.run()
