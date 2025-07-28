import streamlit as st
import streamlit.components.v1 as htmlviewer
# title msg1#
st.title('This is SONG WEBAPP!!')

with open('./indexfinal.html', 'r', encoding='utf-8') as f:
    html = f.read()

#html = '''
#<html>
#    <head>
#        <title> this is my html </title>
#    </head>
#    <body>
#        <h1>Topic</h1>
#        <h2>SubTopic</h2>
#    </body>
#</html>
#'''

# Box#1(4), Box#2(1)
col1, col2 = st.columns((4, 1))

with col1:
    with st.expander('Content #1...'):
        url = 'https://www.youtube.com/watch?v=XyEOEBsa8I4'
        st.info('Content..')
        st.video(url)

    with st.expander('Content #2...'):
        with open('indexfinal.html', 'r', encoding='utf-8') as f:
            other_html = f.read()
        htmlviewer.html(other_html, height=1000)

    with st.expander('Content #3...'):
        with open('index.html', 'r', encoding='utf-8') as f:
            other_html = f.read()
        htmlviewer.html(other_html, height=1000)


with col2:
    with st.expander('Tips..'):
        st.info('Tips..')

st.markdown('<hr>', unsafe_allow_html=True)
st.write('<font color="BLUE">(c)copyright. all rights reserved by Song', unsafe_allow_html=True)