import streamlit as st
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
import yaml

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    auto_hash=False
)


st.title("🧙주식마법사입니다🧙")
if not st.session_state['authentication_status']:
    st.write('로그인을 해주세요')


# Creating a login widget
res = authenticator.login()


if st.session_state['authentication_status']:
    st.write('___')
    st.write(f'안녕하세요 *{st.session_state["name"]}* 님')
    authenticator.logout()
elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')

with open('../config.yaml', 'w') as file:
    yaml.dump(config, file, default_flow_style=False)