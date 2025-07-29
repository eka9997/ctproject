import streamlit as st
import base64

st.set_page_config(layout='wide', page_title='Math problem!!!')

# ✅ 배경 이미지 설정
def get_base64_image(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

bg_image = get_base64_image("images/background.jpeg")

# ✅ CSS 스타일
custom_css = f"""
<style>
.stApp {{
  background: 
    linear-gradient(rgba(0, 0, 0, 0.05), rgba(0, 0, 0, 0.05)),
    url("data:image/jpeg;base64,{bg_image}");
  background-size: cover;
  background-repeat: no-repeat;
  background-attachment: fixed;
  background-position: center;
}}

/* ✅ Expander 헤더 스타일 */
div[data-testid="stExpander"] > div > button {{
    padding-top: 25px !important;  /* 상단 패딩 */
    padding-bottom: 25px !important;  /* 하단 패딩 */
    min-height: 70px;  /* Expander 높이 */
    border-radius: 12px;
    background-color: rgba(255, 255, 255, 0.95) !important;
    border: 2px solid rgba(0, 0, 0, 0.2);
    box-shadow: 0px 6px 15px rgba(0, 0, 0, 0.25);
    transition: background-color 0.3s ease, transform 0.2s ease;
}}

div[data-testid="stExpander"] > div > button:hover {{
    background-color: rgba(255, 255, 255, 1) !important;
    transform: scale(1.03);
}}

/* ✅ 헤더 글씨 크기 */
div[data-testid="stExpander"] > div > button p {{
    font-size: 40px !important;
    font-weight: bold !important;
    color: black !important;
}}

/* ✅ Expander 내용 스타일 */
div[data-testid="stExpander"] .streamlit-expanderContent {{
    font-size: 28px !important;
    color: black !important;
    padding: 20px !important;
    background-color: rgba(255, 255, 255, 0.9) !important;
    border-radius: 10px;
}}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# ---------------- Main Layout ---------------- #
st.title('This is SONG WEBAPP!!')

col1, col2 = st.columns((4, 1))
with col1:
    with st.expander('Content #1...'):
        st.info('Content..')
    with st.expander('Content #2...'):
        st.info('Content..')
    with st.expander('Content #3...'):
        st.info('Content..')
    with st.expander('Image Content #1...'):
        st.info('Image Gallery')

with col2:
    with st.expander('Tips..'):
        st.info('Tips..')

st.markdown('<hr>', unsafe_allow_html=True)
st.write('<font color="BLUE">(c)copyright. all rights reserved by Song', unsafe_allow_html=True)






