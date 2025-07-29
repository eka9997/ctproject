import streamlit as st
import streamlit.components.v1 as htmlviewer
import base64

st.set_page_config(layout='wide', page_title='Math problem!!!')

# ✅ 이미지 → Base64 변환 함수
def get_base64_image(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# 변환된 이미지 리스트
img1 = get_base64_image("images/math1.png")
img2 = get_base64_image("images/math2.png")
img3 = get_base64_image("images/math3.png")

images = [
    f"data:image/png;base64,{img1}",
    f"data:image/png;base64,{img2}",
    f"data:image/png;base64,{img3}"
]

# HTML + JS Lightbox 코드
custom_html = f"""
<html>
<head>
<style>
.gallery img {{
    width: 150px;
    margin: 5px;
    cursor: pointer;
    border-radius: 8px;
    transition: transform 0.2s;
}}
.gallery img:hover {{ transform: scale(1.05); }}
.lightbox {{
    display: none;
    position: fixed;
    z-index: 999;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.9);
    text-align: center;
}}
.lightbox img {{
    max-width: 80%;
    max-height: 80%;
    margin-top: 60px;
}}
.close {{
    position: absolute;
    top: 20px;
    right: 35px;
    color: white;
    font-size: 40px;
    cursor: pointer;
}}
.prev, .next {{
    cursor: pointer;
    position: absolute;
    top: 50%;
    width: auto;
    padding: 16px;
    color: white;
    font-size: 30px;
}}
.prev {{ left: 10%; }}
.next {{ right: 10%; }}
</style>
</head>
<body>
<div class="gallery">
    <img src="{images[0]}" onclick="openLightbox(0)">
    <img src="{images[1]}" onclick="openLightbox(1)">
    <img src="{images[2]}" onclick="openLightbox(2)">
</div>
<div id="myLightbox" class="lightbox">
    <span class="close" onclick="closeLightbox()">&times;</span>
    <a class="prev" onclick="changeSlide(-1)">&#10094;</a>
    <img id="lightboxImage">
    <a class="next" onclick="changeSlide(1)">&#10095;</a>
</div>
<script>
var images = {images};
var currentIndex = 0;
function openLightbox(index) {{
    currentIndex = index;
    document.getElementById('lightboxImage').src = images[index];
    document.getElementById('myLightbox').style.display = 'block';
}}
function closeLightbox() {{
    document.getElementById('myLightbox').style.display = 'none';
}}
function changeSlide(n) {{
    currentIndex += n;
    if (currentIndex >= images.length) currentIndex = 0;
    if (currentIndex < 0) currentIndex = images.length - 1;
    document.getElementById('lightboxImage').src = images[currentIndex];
}}
</script>
</body>
</html>
"""

# ---------------- Main Layout ---------------- #

st.title('This is SONG WEBAPP!!')

with open('./indexfinal.html', 'r', encoding='utf-8') as f:
    html = f.read()

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

    # ✅ 이미지 Lightbox 추가
    with st.expander('Image Content #1...'):
        htmlviewer.html(custom_html, height=600)

with col2:
    with st.expander('Tips..'):
        st.info('Tips..')

st.markdown('<hr>', unsafe_allow_html=True)
st.write('<font color="BLUE">(c)copyright. all rights reserved by Song', unsafe_allow_html=True)

