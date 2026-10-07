import streamlit as st
import requests
import json
from typing import Optional


# ============================================================
# CONFIG
# ============================================================

API_URL = "https://ecard-pregnancy-agenda.ngrok-free.dev"

st.set_page_config(
    page_title="AI Personal Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        background: linear-gradient(
            135deg,
            rgba(99,102,241,0.14),
            rgba(168,85,247,0.10)
        );
        border: 1px solid rgba(128,128,128,0.18);
    }

    .hero h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    .hero p {
        font-size: 1.1rem;
        opacity: 0.75;
        margin-bottom: 0;
    }

    .status-card {
        padding: 1rem 1.2rem;
        border-radius: 14px;
        border: 1px solid rgba(128,128,128,0.18);
        background: rgba(128,128,128,0.05);
        margin-bottom: 1rem;
    }

    .chat-user {
        background: rgba(99,102,241,0.12);
        padding: 1rem 1.2rem;
        border-radius: 16px;
        margin: 0.5rem 0;
    }

    .chat-tutor {
        background: rgba(128,128,128,0.08);
        padding: 1rem 1.2rem;
        border-radius: 16px;
        margin: 0.5rem 0 1rem 0;
    }

    .feature-card {
        padding: 1.2rem;
        border-radius: 16px;
        border: 1px solid rgba(128,128,128,0.18);
        background: rgba(128,128,128,0.04);
        height: 100%;
    }

    .small-muted {
        opacity: 0.65;
        font-size: 0.9rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "last_quiz" not in st.session_state:
    st.session_state.last_quiz = None

if "last_evaluation" not in st.session_state:
    st.session_state.last_evaluation = None

if "api_online" not in st.session_state:
    st.session_state.api_online = False


# ============================================================
# HELPERS
# ============================================================
def api_request(method: str, endpoint: str, **kwargs):
    """
    Centralized API request handler.
    """

    url = f"{API_URL}{endpoint}"

    try:
        # Use timeout from kwargs if provided.
        # Otherwise default to 180 seconds.
        timeout = kwargs.pop("timeout", 180)

        response = requests.request(method, url, timeout=timeout, **kwargs)

        try:
            data = response.json()
        except Exception:
            data = {"detail": response.text}

        if response.status_code != 200:
            error_detail = data.get("detail", "Unknown server error.")

            if isinstance(error_detail, dict):
                error_message = error_detail.get("error", str(error_detail))

            else:
                error_message = str(error_detail)

            return None, (f"API Error ({response.status_code}): {error_message}")

        return data, None

    except requests.exceptions.Timeout:
        return None, (
            "The request took too long. "
            "The AI model may still be processing "
            "your request."
        )

    except requests.exceptions.ConnectionError:
        return None, (
            "Could not connect to the AI Tutor backend. "
            "Make sure the Kaggle API and ngrok are running."
        )

    except Exception as e:
        return None, str(e)


def check_api():

    try:
        response = requests.get(f"{API_URL}/", timeout=15)

        return response.status_code == 200

    except Exception:
        return False


def reset_session():

    st.session_state.session_id = None
    st.session_state.uploaded_files = []
    st.session_state.chat_messages = []
    st.session_state.last_quiz = None
    st.session_state.last_evaluation = None


def render_chat_message(role, content):

    if role == "user":
        st.markdown(
            f"""
            <div class="chat-user">
                <strong>👤 You</strong>
                <br><br>
                {content}
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:
        st.markdown(
            f"""
            <div class="chat-tutor">
                <strong>🎓 AI Tutor</strong>
                <br><br>
                {content}
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 🎓 AI Personal Tutor")

    st.caption("Your personal AI-powered learning assistant")

    st.divider()

    # --------------------------------------------------------
    # API STATUS
    # --------------------------------------------------------

    if st.button("🔄 Check Backend", use_container_width=True):
        st.session_state.api_online = check_api()

    if st.session_state.api_online:
        st.success("Backend Online")

    else:
        st.warning("Backend status not checked")

    st.divider()

    # --------------------------------------------------------
    # SESSION
    # --------------------------------------------------------

    st.markdown("### 📚 Current Session")

    if st.session_state.session_id:
        st.success("PDF loaded")

        st.caption(f"Session: {st.session_state.session_id[:12]}...")

        if st.session_state.uploaded_files:
            st.markdown("**Files:**")

            for filename in st.session_state.uploaded_files:
                st.caption(f"📄 {filename}")

    else:
        st.info("Upload educational material to start learning.")

    st.divider()

    if st.button("🗑️ Start New Session", use_container_width=True):
        reset_session()

        st.rerun()

    st.divider()

    st.caption("Backend: Kaggle + FastAPI + Qwen")

    st.caption("Frontend: Streamlit")


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">

        <h1>🎓 AI Personal Tutor</h1>

        <p>
            Upload your lecture material and learn through
            explanation, conversation, quizzes and evaluation.
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# NO SESSION → UPLOAD
# ============================================================

if not st.session_state.session_id:
    st.subheader("📚 Start a Learning Session")

    st.write("Upload one or more PDF lectures to build your personal learning session.")

    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        help="You can upload one or multiple PDF lectures.",
    )

    if uploaded_files:
        st.write(f"**{len(uploaded_files)} file(s) selected**")

        for file in uploaded_files:
            st.caption(f"📄 {file.name} — {file.size / 1024:.1f} KB")

        if st.button("🚀 Start Learning", type="primary", use_container_width=True):
            with st.spinner("Uploading and processing your material..."):
                files_payload = []

                for file in uploaded_files:
                    files_payload.append(
                        ("files", (file.name, file.getvalue(), "application/pdf"))
                    )

                result, error = api_request(
                    "POST", "/upload", files=files_payload, timeout=180
                )

            if error:
                st.error(error)

                st.info(
                    "Make sure your Kaggle backend is running "
                    "and your ngrok URL is still active."
                )

            else:
                st.session_state.session_id = result["session_id"]

                st.session_state.uploaded_files = [file.name for file in uploaded_files]

                st.success("Your learning session is ready! 🎉")

                st.rerun()

    else:
        st.markdown("### What you can do")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                """
                <div class="feature-card">

                ### 💡 Explain

                Get clear explanations of
                concepts from your lectures.

                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                """
                <div class="feature-card">

                ### 🧠 Quiz

                Generate questions to test
                your actual understanding.

                </div>
                """,
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                """
                <div class="feature-card">

                ### 📝 Evaluate

                Submit your answer and get
                an AI evaluation.

                </div>
                """,
                unsafe_allow_html=True,
            )

        with col4:
            st.markdown(
                """
                <div class="feature-card">

                ### 💬 Chat

                Discuss the lecture naturally
                with your AI tutor.

                </div>
                """,
                unsafe_allow_html=True,
            )

    st.stop()


# ============================================================
# MAIN APPLICATION
# ============================================================

tabs = st.tabs(["💬 AI Tutor", "💡 Explain", "🧠 Quiz", "📝 Evaluate"])


# ============================================================
# CHAT
# ============================================================

with tabs[0]:
    st.subheader("💬 AI Tutor")

    st.caption(
        "Ask questions, request explanations, "
        "ask about the lecture, or continue the conversation."
    )

    if not st.session_state.chat_messages:
        st.info('Try asking: "What are the main topics covered in this lecture?"')

    else:
        for message in st.session_state.chat_messages:
            render_chat_message(message["role"], message["content"])

    user_message = st.chat_input("Ask your tutor anything...")

    if user_message:
        st.session_state.chat_messages.append({"role": "user", "content": user_message})

        render_chat_message("user", user_message)

        with st.spinner("🎓 Your tutor is thinking..."):
            result, error = api_request(
                "POST",
                "/chat",
                json={
                    "session_id": st.session_state.session_id,
                    "message": user_message,
                },
            )

        if error:
            st.error(error)

        else:
            answer = result.get("answer", "No answer returned.")

            st.session_state.chat_messages.append(
                {"role": "assistant", "content": answer}
            )

            render_chat_message("assistant", answer)


# ============================================================
# EXPLAIN
# ============================================================

with tabs[1]:
    st.subheader("💡 Explain a Concept")

    st.write("Choose a topic from your material and get a structured explanation.")

    topic = st.text_input("Topic", placeholder="e.g. Quantization")

    if st.button("Explain Topic", type="primary"):
        if not topic.strip():
            st.warning("Please enter a topic first.")

        else:
            with st.spinner("Preparing your explanation..."):
                result, error = api_request(
                    "POST",
                    "/explain",
                    json={"session_id": st.session_state.session_id, "topic": topic},
                )

            if error:
                st.error(error)

            else:
                st.success("Explanation generated.")

                st.markdown(f"### {result.get('topic', topic)}")

                st.write(result.get("explanation", ""))

                example = result.get("example")

                if example:
                    st.markdown("### 🔎 Example")

                    st.info(example)

                key_points = result.get("key_points", [])

                if key_points:
                    st.markdown("### 📌 Key Points")

                    for point in key_points:
                        st.markdown(f"- {point}")


# ============================================================
# QUIZ
# ============================================================

with tabs[2]:
    st.subheader("🧠 Test Your Understanding")

    st.write("Generate 5 questions based on the educational material.")

    quiz_topic = st.text_input(
        "Quiz Topic", placeholder="e.g. Digital Image Processing", key="quiz_topic"
    )

    if st.button("Generate Quiz", type="primary"):
        if not quiz_topic.strip():
            st.warning("Please enter a topic first.")

        else:
            with st.spinner("Creating your quiz..."):
                result, error = api_request(
                    "POST",
                    "/quiz",
                    json={
                        "session_id": st.session_state.session_id,
                        "topic": quiz_topic,
                    },
                )

            if error:
                st.error(error)

            else:
                st.session_state.last_quiz = result

    if st.session_state.last_quiz:
        quiz = st.session_state.last_quiz

        st.markdown(f"### 📚 {quiz.get('topic', quiz_topic)}")

        questions = quiz.get("questions", [])

        for index, question in enumerate(questions, start=1):
            st.markdown(f"### Question {index}")

            st.write(question.get("question", ""))

            with st.expander("Show Answer"):
                st.markdown("**Answer**")

                st.write(question.get("answer", ""))

                st.markdown("**Explanation**")

                st.write(question.get("explanation", ""))

                difficulty = question.get("difficulty", "")

                if difficulty:
                    st.caption(f"Difficulty: {difficulty}")


# ============================================================
# EVALUATION
# ============================================================

with tabs[3]:
    st.subheader("📝 Evaluate My Answer")

    st.write(
        "Compare your answer against the reference answer "
        "and receive a score with strengths and weaknesses."
    )

    question = st.text_area("Question", placeholder="Enter the question...", height=100)

    reference_answer = st.text_area(
        "Reference Answer",
        placeholder="Enter the correct/reference answer...",
        height=150,
    )

    student_answer = st.text_area(
        "Your Answer", placeholder="Write your answer here...", height=180
    )

    if st.button("Evaluate Answer", type="primary"):
        if not question.strip():
            st.warning("Please enter the question.")

        elif not reference_answer.strip():
            st.warning("Please enter the reference answer.")

        elif not student_answer.strip():
            st.warning("Please enter your answer.")

        else:
            with st.spinner("Evaluating your answer..."):
                result, error = api_request(
                    "POST",
                    "/evaluate",
                    json={
                        "session_id": st.session_state.session_id,
                        "question": question,
                        "reference_answer": reference_answer,
                        "student_answer": student_answer,
                    },
                )

            if error:
                st.error(error)

            else:
                st.session_state.last_evaluation = result

    if st.session_state.last_evaluation:
        evaluation = st.session_state.last_evaluation

        st.divider()

        st.markdown("## 📊 Evaluation")

        score = evaluation.get("score", 0)

        grade = evaluation.get("grade", "")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Score", f"{score}/100")

        with col2:
            st.metric("Grade", grade)

        feedback = evaluation.get("feedback", "")

        if feedback:
            st.markdown("### 💬 Feedback")

            st.info(feedback)

        strengths = evaluation.get("strengths", [])

        if strengths:
            st.markdown("### ✅ Strengths")

            for item in strengths:
                st.markdown(f"- {item}")

        weaknesses = evaluation.get("weaknesses", [])

        if weaknesses:
            st.markdown("### ⚠️ Areas to Improve")

            for item in weaknesses:
                st.markdown(f"- {item}")

        model_answer = evaluation.get("model_answer", "")

        if model_answer:
            with st.expander("📖 View Model Answer"):
                st.write(model_answer)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption("AI Personal Tutor • RAG-based educational assistant")

st.caption(f"Connected API: {API_URL}")
