import warnings
warnings.filterwarnings("ignore")

import streamlit as st
from utils.file_parser import extract_text_from_pdf, extract_text_from_docx
from utils.quiz_generator import generate_quiz, parse_quiz_to_dict
from utils.gemini_rag import GeminiRAG

# Initialize RAG
rag = GeminiRAG()

st.set_page_config(page_title="LearniFy", layout="wide")
st.title("📚 LearniFy – Smart Chat & Quiz Generator")

uploaded_file = st.file_uploader("📄 Upload a PDF or DOCX", type=["pdf", "docx"])

if uploaded_file:
    file_text = ""
    if uploaded_file.type == "application/pdf":
        file_text = extract_text_from_pdf(uploaded_file)
    else:
        file_text = extract_text_from_docx(uploaded_file)

    st.success("✅ Document processed successfully!")
    rag.build_index(file_text)

    tab1, tab2 = st.tabs(["💬 Ask Questions", "📝 Generate Quiz"])

    # === CHAT TAB ===
    with tab1:
        user_q = st.text_input("Ask a question about your document:")
        if user_q:
            with st.spinner("Thinking..."):
                answer = rag.ask(user_q)
            st.markdown(f"**Answer:**\n{answer}")

    # === QUIZ TAB ===
    with tab2:
        num = st.slider("Number of Questions", 1, 10, 5)
        difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"])

        if st.button("Generate Quiz"):
            with st.spinner("Generating quiz..."):
                quiz_text = generate_quiz(file_text, num, difficulty)
                # st.text_area("🪵 Raw AI Output", quiz_text, height=300)  # <== TEMP DEBUG
                st.session_state.quiz_data = parse_quiz_to_dict(quiz_text)
                st.session_state.submitted = False

        

        if "quiz_data" in st.session_state:
            st.subheader("🧠 Take the Quiz")

            user_answers = {}
            for i, q in enumerate(st.session_state.quiz_data):
                st.markdown(f"**Q{i+1}: {q['question']}**")
                user_answers[i] = st.radio(
                    label="Choose your answer:",
                    options=list(q["options"].keys()),
                    format_func=lambda x: f"{x}. {q['options'][x]}",
                    key=f"q{i}"
                )
                st.markdown("---")

            if st.button("Submit Quiz"):
                st.session_state.submitted = True
                score = 0
                for i, q in enumerate(st.session_state.quiz_data):
                    selected = user_answers[i]
                    correct = q["correct"]
                    if selected == correct:
                        score += 1
                st.success(f"✅ You scored {score} out of {len(st.session_state.quiz_data)}")

            if st.session_state.get("submitted", False):
                st.markdown("### ✅ Correct Answers")
                for i, q in enumerate(st.session_state.quiz_data):
                    correct = q["correct"]
                    st.markdown(f"**Q{i+1}: {q['question']}**")
                    st.markdown(f"- ✅ Correct: **{correct}. {q['options'][correct]}**")
                    st.markdown("---")

else:
    st.info("📂 Please upload a file to get started.")
