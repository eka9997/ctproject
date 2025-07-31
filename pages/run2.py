import streamlit as st
import pandas as pd
import numpy as np
import os
import joblib
import pytesseract
from PIL import Image
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- CONFIG ---------------- #
ANSWER_FILE = "ml_answers.csv"
STUDENT_FILE = "ml_students.csv"
MODEL_FILE = "grading_model.pkl"
TOTAL_Q_FILE = "total_questions.txt"

st.set_page_config(layout='wide', page_title='머신러닝 기반 AI 채점기 (최적화)')

# ✅ SBERT 모델 캐싱
@st.cache_resource
def load_sbert():
    return SentenceTransformer("jhgan/ko-sroberta-multitask")

sbert_model = load_sbert()

# ✅ OCR 함수
def extract_text(file):
    img = Image.open(file).convert("L")
    img = img.resize((img.width // 2, img.height // 2))
    return pytesseract.image_to_string(img, lang="kor+eng").strip()

# ✅ 성취 수준
def get_level(score):
    if score >= 80:
        return "상"
    elif score >= 50:
        return "중"
    else:
        return "하"

# ✅ 임베딩 캐싱
@st.cache_data
def get_embedding(text):
    return sbert_model.encode([text])[0]

# ✅ 임베딩 계산 후 CSV에 저장
def save_answer_with_embeddings(answers):
    answers["임베딩"] = answers["정답"].apply(lambda x: get_embedding(x).tolist())
    answers.to_csv(ANSWER_FILE, index=False)

# ---------------- 메뉴 ---------------- #
menu = st.sidebar.radio("📌 메뉴", ["🏠 홈", "🛠️ 정답 관리/학습", "✍️ 풀이 제출", "🤖 AI 채점"])

# ---------------- 홈 ---------------- #
if menu == "🏠 홈":
    st.title("🚀 머신러닝 + SBERT 기반 AI 채점기 (최적화)")
    st.write("""
    - SBERT 문장 임베딩 캐싱
    - 정답 임베딩 사전 계산 → 빠른 채점
    - 머신러닝 모델(Logistic Regression) 학습·저장
    """)

# ---------------- 정답 관리 + 학습 ---------------- #
elif menu == "🛠️ 정답 관리/학습":
    st.header("🛠️ 교사 정답 관리 및 학습")
    total_questions = st.number_input("총 문항 수", min_value=1, max_value=20, value=5)
    with open(TOTAL_Q_FILE, "w") as f:
        f.write(str(total_questions))

    answers = pd.read_csv(ANSWER_FILE) if os.path.exists(ANSWER_FILE) else pd.DataFrame(columns=["문항", "정답", "점수", "임베딩"])

    for i in range(total_questions):
        ans = st.text_area(f"문항 {i+1} 정답", key=f"teacher_ans_{i}")
        score = st.slider(f"문항 {i+1} 점수", 0, 100, 100, key=f"teacher_score_{i}")
        if ans:
            emb = get_embedding(ans).tolist()
            if (answers["문항"] == i+1).any():
                answers.loc[answers["문항"] == i+1, ["정답", "점수", "임베딩"]] = [ans, score, emb]
            else:
                answers = pd.concat([answers, pd.DataFrame([[i+1, ans, score, emb]], 
                                                           columns=["문항", "정답", "점수", "임베딩"])], ignore_index=True)

    if st.button("💾 정답 저장"):
        save_answer_with_embeddings(answers)
        st.success("정답 및 임베딩이 저장되었습니다.")

    if not answers.empty:
        st.dataframe(answers.drop(columns=["임베딩"]))

    if st.button("🤖 머신러닝 모델 학습"):
        if not answers.empty:
            X = np.vstack(answers["임베딩"].values)
            y = answers["점수"].values
            clf = LogisticRegression(max_iter=1000)
            clf.fit(X, y)
            joblib.dump(clf, MODEL_FILE)
            st.success("모델 학습이 완료되었습니다.")
        else:
            st.warning("⚠️ 학습할 데이터가 없습니다.")

# ---------------- 학생 풀이 제출 ---------------- #
elif menu == "✍️ 풀이 제출":
    st.header("✍️ 학생 풀이")
    student_name = st.text_input("학생 이름")
    student_id = st.text_input("학번")

    if os.path.exists(TOTAL_Q_FILE):
        with open(TOTAL_Q_FILE, "r") as f:
            total_questions = int(f.read().strip())
    else:
        st.warning("⚠️ 교사가 먼저 문항 수를 설정하세요.")
        total_questions = 0

    students = pd.read_csv(STUDENT_FILE) if os.path.exists(STUDENT_FILE) else pd.DataFrame(columns=["학번", "이름", "문항", "풀이"])

    for i in range(total_questions):
        ans = st.text_area(f"문항 {i+1} 풀이", key=f"student_ans_{i}")
        img = st.file_uploader(f"문항 {i+1} 이미지", type=["png", "jpg", "jpeg"], key=f"student_img_{i}")
        if img:
            text = extract_text(img)
            st.success(f"OCR 추출: {text[:30]}...")
            ans = text

        if ans:
            new_data = pd.DataFrame([[student_id, student_name, i+1, ans]], 
                                    columns=["학번", "이름", "문항", "풀이"])
            students = pd.concat([students, new_data], ignore_index=True)

    if st.button("💾 제출"):
        students.to_csv(STUDENT_FILE, index=False)
        st.success("풀이가 저장되었습니다.")

    if not students.empty:
        st.dataframe(students)

# ---------------- AI 채점 ---------------- #
elif menu == "🤖 AI 채점":
    st.header("🤖 AI 자동 채점")
    if not os.path.exists(ANSWER_FILE) or not os.path.exists(STUDENT_FILE):
        st.warning("⚠️ 정답과 학생 풀이가 필요합니다.")
    else:
        answers = pd.read_csv(ANSWER_FILE)
        students = pd.read_csv(STUDENT_FILE)
        merged = pd.merge(students, answers[["문항", "정답", "임베딩"]], how="left", on="문항")

        # 학생 풀이 임베딩 계산
        student_embeddings = np.vstack([get_embedding(x) for x in merged["풀이"]])
        answer_embeddings = np.vstack(merged["임베딩"].apply(eval))  # 문자열 → 리스트 → numpy

        # SBERT 유사도
        similarities = cosine_similarity(student_embeddings, answer_embeddings)
        merged["유사도"] = [similarities[i][i] for i in range(len(merged))]

        # ML 모델 예측
        if os.path.exists(MODEL_FILE):
            clf = joblib.load(MODEL_FILE)
            ml_scores = clf.predict(student_embeddings)
            merged["ML 점수"] = ml_scores
            merged["최종 점수"] = (merged["유사도"] * 50 + ml_scores * 0.5).round(1)
        else:
            merged["ML 점수"] = merged["유사도"] * 100
            merged["최종 점수"] = merged["ML 점수"]

        merged["성취 수준"] = merged["최종 점수"].apply(get_level)

        st.dataframe(merged[["학번", "이름", "문항", "유사도", "ML 점수", "최종 점수", "성취 수준"]])
        st.bar_chart(merged.groupby("문항")["최종 점수"].mean())


