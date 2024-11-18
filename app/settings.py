import streamlit as st

st.title('세팅')


st.header('내정보')
st.write('내 계정:',st.session_state['name'])
st.write('내 이메일:',st.session_state['email'])
