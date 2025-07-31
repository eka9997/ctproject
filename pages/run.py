import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import os
from fpdf import FPDF
import matplotlib.pyplot as plt
from io import BytesIO
import random

# CSV 파일 경로
ANSWER_FILE = "answers.csv"
STUDENT_FILE = "student_answers.csv"
TOTAL_Q_FILE = "total_questions.txt"

st.set_page_config(layout='wide', page_title='AI CT 자동 채점 시스템')

menu = st.sidebar.radio("📌 메뉴", ["🏠 홈", "🛠️ 정답 관리", "✍️ 풀이 제출", "🤖 AI 채점", "📄 PDF 리포트"])

# ✅ OCR 함수 (이미지 축소 + 그레이스케일 변환)
def extract_text(file):
    img = Image.open(file).convert("L")  # Grayscale
    img = img.resize((img.width // 2, img.height // 2))  # 크기 절반 축소
    return pytesseract.image_to_string(img, lang="kor+eng").strip()

# ✅ 성취 수준
def get_level(score):
    if score >= 80:
        return "상"
    elif score >= 50:
        return "중"
    else:
        return "하"

# ✅ CT 요소 점수 시뮬레이션
def calculate_ct_scores(text):
    keywords = {
        "문제분해": ["조건", "단계", "부분"],
        "패턴인식": ["패턴", "규칙", "반복"],
        "추상화": ["공식", "정리", "단순화"],
        "알고리즘": ["순서", "절차", "흐름"]
    }
    scores = {}
    for ct, kws in keywords.items():
        scores[ct] = min(100, sum(text.count(k) for k in kws) * 10 + random.randint(50, 80))
    return scores

# ✅ PDF 클래스
class ReportPDF(FPDF):
    def header(self):
        if os.path.exists("school_logo.png"):
            self.image("school_logo.png", 10, 8, 20)
        self.set_font("Arial", 'B', 16)
        self.cell(0, 10, "AI 기반 CT 문제 자동 채점 리포트", ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", 'I', 10)
        self.cell(0, 10, f"페이지 {self.page_no()}", align='C')

# ✅ PDF 생성 (BytesIO 사용)
def create_advanced_pdf(df, file_name, student_name=None):
    pdf = ReportPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    if student_name:
        pdf.cell(0, 10, f"학생 이름: {student_name}", ln=True)
        학번 = df["학번"].values[0] if "학번" in df.columns else "-"
        pdf.cell(0, 10, f"학번: {학번}", ln=True)

    pdf.ln(5)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(30, 10, "문항", 1, 0, 'C', fill=True)
    pdf.cell(40, 10, "점수(%)", 1, 0, 'C', fill=True)
    pdf.cell(40, 10, "성취 수준", 1, 1, 'C', fill=True)

    for _, row in df.iterrows():
        pdf.cell(30, 10, str(row["문항"]), 1, 0, 'C')
        pdf.cell(40, 10, f"{row['점수']}", 1, 0, 'C')
        level_color = {"상": (0, 200, 0), "중": (255, 165, 0), "하": (255, 0, 0)}
        r, g, b = level_color.get(row["성취 수준"], (0, 0, 0))
        pdf.set_text_color(r, g, b)
        pdf.cell(40, 10, row["성취 수준"], 1, 1, 'C')
        pdf.set_text_color(0, 0, 0)

    # 문항별 점수 그래프 (BytesIO로 메모리에서 처리)
    buf1 = BytesIO()
    plt.figure(figsize=(4, 2))
    df["점수"].plot(kind='bar', color='skyblue')
    plt.title("문항별 점수 분포")
    plt.ylabel("점수(%)")
    plt.tight_layout()
    plt.savefig(buf1, format="png")
    plt.close()
    buf1.seek(0)
    pdf.image(buf1, x=60, w=90)

    # CT 요소별 점수 분석 그래프
    buf2 = BytesIO()
    ct_scores = calculate_ct_scores(" ".join(df["풀이"]))
    plt.figure(figsize=(4, 2))
    plt.bar(ct_scores.keys(), ct_scores.values(), color=['blue', 'green', 'orange', 'purple'])
    plt.title("CT 요소별 점수 분석")
    plt.ylabel("점수(%)")
    plt.tight_layout()
    plt.savefig(buf2, format="png")
    plt.close()
    buf2.seek(0)
    pdf.ln(50)
    pdf.image(buf2, x=60, w=90)

    pdf.ln(60)
    pdf.multi_cell(0, 10, "📌 교사 코멘트:\n학생의 CT 요소 이해도와 문제 해결 능력이 향상되고 있습니다. "
                          "성취 수준이 낮은 부분은 피드백을 바탕으로 추가 학습을 권장합니다.\n\n"
                          "교사 서명: _____________________")

    pdf.output(file_name)
    return file_name

# ---------------- 홈 ---------------- #
if menu == "🏠 홈":
    st.title("🤖 AI 기반 CT 문제 자동 채점")
    st.write("교사와 학생이 Drag & Drop으로 답안을 제출하면 AI가 자동 채점하고 성취 수준 및 CT 분석을 제공합니다.")

# ---------------- 교사: 정답 관리 ---------------- #
elif menu == "🛠️ 정답 관리":
    st.header("🛠️ 정답 파일 관리")
    total_questions = st.number_input("총 평가 문항 수", min_value=1, max_value=20, value=5)
    with open(TOTAL_Q_FILE, "w") as f:
        f.write(str(total_questions))
    st.info(f"총 {total_questions} 문항이 설정되었습니다.")

    answers = pd.read_csv(ANSWER_FILE) if os.path.exists(ANSWER_FILE) else pd.DataFrame(columns=["문항", "정답"])
    cols = st.columns(3)  # 한 줄에 3개만 표시
    for i in range(total_questions):
        with cols[i % 3]:
            file = st.file_uploader(f"문항 {i+1} 정답 업로드", type=["png", "jpg", "jpeg"], key=f"file_teacher_{i}")
            if file:
                text = extract_text(file)
                st.success(f"정답 추출: {text[:30]}...")
                if (answers["문항"] == i+1).any():
                    answers.loc[answers["문항"] == i+1, "정답"] = text
                else:
                    answers = pd.concat([answers, pd.DataFrame([[i+1, text]], columns=["문항", "정답"])], ignore_index=True)
                answers.to_csv(ANSWER_FILE, index=False)
                st.info("정답이 저장되었습니다.")

    if not answers.empty:
        st.dataframe(answers)

# ---------------- 학생: 풀이 제출 ---------------- #
elif menu == "✍️ 풀이 제출":
    st.header("✍️ 학생 풀이 업로드")
    student_name = st.text_input("학생 이름")
    student_id = st.text_input("학번")

    if os.path.exists(TOTAL_Q_FILE):
        with open(TOTAL_Q_FILE, "r") as f:
            total_questions = int(f.read().strip())
    else:
        st.warning("⚠️ 교사가 먼저 문항 수를 설정해야 합니다.")
        total_questions = 0

    if total_questions > 0:
        cols = st.columns(3)
        student_df = pd.read_csv(STUDENT_FILE) if os.path.exists(STUDENT_FILE) else pd.DataFrame(columns=["학번", "이름", "문항", "풀이"])
        for i in range(total_questions):
            with cols[i % 3]:
                file = st.file_uploader(f"문항 {i+1} 답안 업로드", type=["png", "jpg", "jpeg"], key=f"file_student_{i}")
                if file:
                    text = extract_text(file)
                    st.success(f"풀이 추출: {text[:30]}...")
                    if ((student_df["학번"] == student_id) & (student_df["문항"] == i+1)).any():
                        student_df.loc[(student_df["학번"] == student_id) & (student_df["문항"] == i+1), "풀이"] = text
                    else:
                        new_data = pd.DataFrame([[student_id, student_name, i+1, text]], columns=["학번", "이름", "문항", "풀이"])
                        student_df = pd.concat([student_df, new_data], ignore_index=True)
                    student_df.to_csv(STUDENT_FILE, index=False)
                    st.info("풀이가 저장되었습니다.")

        if not student_df.empty:
            st.dataframe(student_df)

# ---------------- AI 채점 ---------------- #
elif menu == "🤖 AI 채점":
    st.header("🤖 AI 자동 채점 결과")
    if not os.path.exists(ANSWER_FILE) or not os.path.exists(STUDENT_FILE):
        st.warning("⚠️ 정답과 학생 풀이가 모두 있어야 합니다.")
    else:
        answers = pd.read_csv(ANSWER_FILE)
        students = pd.read_csv(STUDENT_FILE)
        merged = pd.merge(students, answers, how="left", on="문항")
        merged["점수"] = merged.apply(lambda row: round(len(set(row["풀이"].split()) & set(row["정답"].split())) / max(len(row["정답"].split()), 1) * 100, 1), axis=1)
        merged["성취 수준"] = merged["점수"].apply(get_level)
        st.dataframe(merged[["학번", "이름", "문항", "점수", "성취 수준"]])
        avg_scores = merged.groupby("문항")["점수"].mean()
        st.bar_chart(avg_scores)

# ---------------- PDF 리포트 ---------------- #
elif menu == "📄 PDF 리포트":
    st.header("📄 PDF 리포트 다운로드")
    if not os.path.exists(STUDENT_FILE):
        st.warning("⚠️ 학생 풀이 데이터가 없습니다.")
    else:
        students = pd.read_csv(STUDENT_FILE)
        answers = pd.read_csv(ANSWER_FILE)
        merged = pd.merge(students, answers, how="left", on="문항")
        merged["점수"] = merged.apply(lambda row: round(len(set(row["풀이"].split()) & set(row["정답"].split())) / max(len(row["정답"].split()), 1) * 100, 1), axis=1)
        merged["성취 수준"] = merged["점수"].apply(get_level)

        st.subheader("🔹 개별 학생 리포트")
        for student in merged["이름"].unique():
            student_data = merged[merged["이름"] == student]
            file_name = f"{student}_report.pdf"
            create_advanced_pdf(student_data, file_name, student_name=student)
            with open(file_name, "rb") as f:
                st.download_button(f"{student} 리포트 다운로드", f, file_name=file_name)

        st.subheader("🔹 전체 학급 리포트")
        file_name_all = "전체_학급_리포트.pdf"
        create_advanced_pdf(merged, file_name_all)
        with open(file_name_all, "rb") as f:
            st.download_button("전체 학급 리포트 다운로드", f, file_name=file_name_all)


