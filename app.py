import streamlit as st
from src.graph import app
from src.nodes.generator import generate_followups

st.set_page_config(page_title="Agentic RAG Assistant", page_icon="🧠")


st.markdown("""
<style>
/* ── Background ── */
html, body, .stApp,
[data-testid="stAppViewContainer"] {
    background: #1a1830 !important;
}
[data-testid="stMain"],
[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"],
section[data-testid="stBottom"],
section[data-testid="stBottom"] > div,
section[data-testid="stBottom"] > div > div,
section[data-testid="stBottom"] > div > div > div {
    background: transparent !important;
    border-top: none !important;
    box-shadow: none !important;
}

[data-testid="stHeader"] {
    background: rgba(15, 12, 41, 0.85) !important;
    backdrop-filter: blur(8px);
}

/* ── Chat input (FINAL CLEAN VERSION) ── */

[data-testid="stChatInputContainer"] {
    background: rgba(255,255,255,0.07) !important;
    border: 1.5px solid #6C63FF !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
}

/* Darken on typing */
[data-testid="stChatInput"]:focus-within {
    background: rgba(20, 18, 50, 0.95) !important;
}

/* ONLY remove visual noise */
div[data-baseweb="input"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* ✅ UPDATED FONT SIZE HERE */
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    color: white !important;
    font-size: 17px !important;   /* ⬅️ increased */
    line-height: 1.4 !important;  /* ⬅️ better spacing */
}

/* ── Submit button ── */
[data-testid="stChatInputSubmitButton"] {
    background: #6C63FF !important;
    border-radius: 6px !important;
    width: 34px !important;
    height: 34px !important;
}

[data-testid="stChatInputSubmitButton"]:hover {
    background: #5a52e0 !important;
}

[data-testid="stChatInputSubmitButton"] svg {
    fill: #ffffff !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(108, 99, 255, 0.25) !important;
    margin-bottom: 8px;
}

/* ── Markdown text colour ── */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
    color: #e8e6ff !important;
}

/* ── Global font ── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Segoe UI', sans-serif;
}

/* ── Gradient page header ── */
.main-header {
    background: linear-gradient(135deg, #6C63FF 0%, #3ECFCF 100%);
    border-radius: 16px;
    padding: 20px 28px;
    margin-bottom: 24px;
    color: white;
    font-size: 26px;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 12px;
}

/* ── User bubble ── */
.user-bubble {
    display: inline-block;
    max-width: 70%;
    padding: 10px 16px;
    border-radius: 18px 18px 4px 18px;
    background: linear-gradient(135deg, #6C63FF, #9B59B6);
    color: white;
    font-size: 14px;
    margin-bottom: 10px;
}

/* ── Cards ── */
.card {
    padding: 12px 16px;
    border-radius: 12px;
    margin-bottom: 8px;
    border: 1.5px solid rgba(108,99,255,0.35);
    background: rgba(108, 99, 255, 0.08);
    color: #e8e6ff;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(15, 12, 41, 0.95) !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🧠 System Design Assistant</div>', unsafe_allow_html=True)


# 🧠 NEW: VALIDATION FUNCTION
def is_valid_query(query):
    if len(query.strip()) < 5:
        return False
    vowels = set("aeiouAEIOU")
    if not any(char in vowels for char in query):
        return False
    return True


# 🧠 SESSION STATE INIT
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None
if "followups" not in st.session_state:
    st.session_state.followups = []
if "quiz_mode" not in st.session_state:
    st.session_state.quiz_mode = False
if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = []
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "show_feedback" not in st.session_state:
    st.session_state.show_feedback = False
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None
if "score_updated" not in st.session_state:
    st.session_state.score_updated = False


# =========================
# 🔁 DISPLAY CHAT HISTORY
# =========================
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f"""
            <div style='width:100%; text-align:right; margin-bottom:10px;'>
                <div class="user-bubble">{msg['content']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        with st.chat_message("assistant"):
            st.markdown(msg["content"])


# =========================
# 💬 USER INPUT
# =========================
user_input = st.chat_input("Ask a system design question...")

query = user_input or st.session_state.pending_query

if query:
    st.session_state.pending_query = None
    st.session_state.messages.append({"role": "user", "content": query})

    st.markdown(
        f"""
        <div style='width:100%; text-align:right; margin-bottom:10px;'>
            <div class="user-bubble">{query}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 🚨 NEW: VALIDATION CHECK
    if not is_valid_query(query):
        response = """👋 Hey! I’m your AI System Design Assistant.

Try asking:
• Design a URL shortener  
• How does Netflix scale?  
• Design WhatsApp backend  
"""
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    with st.chat_message("assistant"):
        with st.spinner(" Thinking..."):
            result = app.invoke({"query": query})
            st.session_state.last_result = result  # ✅ NEW FIX
            answer = result["answer"]
        st.markdown(answer)

    if "__MCQ__" in answer:
        if "__HIDDEN__" not in answer:
            st.error("MCQ generation failed")
        else:
            visible, hidden = answer.split("__HIDDEN__")
            visible_clean = visible.replace("__MCQ__", "").strip()
            hidden_clean = hidden.strip()
            st.session_state.questions = visible_clean.split("\n\n---\n\n")
            st.session_state.answers = hidden_clean.split("||")
            st.session_state.current_q = 0
            st.session_state.score = 0
            st.session_state.quiz_mode = True
            st.rerun()

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.followups = generate_followups(answer)


# =========================
# 🔁 FOLLOW-UP CHIPS
# =========================
if st.session_state.followups:
    st.markdown('<div class="accent-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="followup-label">🔁 Follow-up Questions</div>', unsafe_allow_html=True)

    cols = st.columns(len(st.session_state.followups))
    for i, q in enumerate(st.session_state.followups):
        with cols[i]:
            if st.button(q, key=f"followup_{i}"):
                st.session_state.pending_query = q
                st.rerun()


# =========================
# 🧪 QUIZ DISPLAY
# =========================
if st.session_state.quiz_mode:

    q_idx = st.session_state.current_q
    questions = st.session_state.questions
    answers = st.session_state.answers

    if q_idx < len(questions):

        st.markdown('<div class="accent-divider"></div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="quiz-header">🧪 Question {q_idx + 1} of {len(questions)}</div>',
            unsafe_allow_html=True
        )

        col_exit, _ = st.columns([1, 5])
        with col_exit:
            if st.button("❌ Exit Quiz"):
                for key in ["quiz_mode", "questions", "answers", "current_q", "score",
                            "show_feedback", "last_result", "selected_option", "score_updated"]:
                    st.session_state[key] = (
                        False if key in ("quiz_mode", "show_feedback", "score_updated")
                        else [] if key in ("questions", "answers")
                        else 0 if key in ("current_q", "score")
                        else None
                    )
                st.rerun()

        progress = (q_idx + 1) / len(questions)
        st.progress(progress)

        q_text = questions[q_idx]
        lines = q_text.split("\n")
        question_part = []
        options = []

        for line in lines:
            line = line.strip()
            if line.startswith(("A.", "B.", "C.", "D.")):
                options.append(line)
            else:
                question_part.append(line)

        st.markdown("\n".join(question_part))

        for opt in options:
            option_letter = opt[0]

            if st.session_state.show_feedback:
                res = st.session_state.last_result
                correct = res["correct"]
                user_choice = res["user_choice"]

                if option_letter == correct:
                    st.markdown(f'<div class="card correct">✅ {opt}</div>', unsafe_allow_html=True)
                elif option_letter == user_choice:
                    st.markdown(f'<div class="card wrong">❌ {opt}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="card">{opt}</div>', unsafe_allow_html=True)
            else:
                if st.button(opt, key=opt):
                    hidden = answers[q_idx]
                    parts = hidden.split("|")
                    correct = parts[0].replace("ANSWER:", "").strip().split(".")[0].upper()
                    explanation = parts[1].replace("EXPLANATION:", "").strip()
                    st.session_state.selected_option = option_letter
                    st.session_state.last_result = {
                        "user_choice": option_letter,
                        "correct": correct,
                        "explanation": explanation
                    }
                    st.session_state.show_feedback = True
                    st.session_state.score_updated = False
                    st.rerun()

        if st.session_state.show_feedback:
            res = st.session_state.last_result

            if res["user_choice"] == res["correct"]:
                st.success("✅ That's right!")
                st.info(f"💡 {res['explanation']}")
                if not st.session_state.score_updated:
                    st.session_state.score += 1
                    st.session_state.score_updated = True
            else:
                st.error(f"❌ You chose {res['user_choice']}")
                st.success(f"✅ Correct Answer: {res['correct']}")
                st.info(f"💡 {res['explanation']}")

            if st.button("Next Question ➡️"):
                st.session_state.current_q += 1
                st.session_state.show_feedback = False
                st.session_state.last_result = None
                st.session_state.selected_option = None
                st.session_state.score_updated = False
                st.rerun()

    else:
        st.markdown(
            f'<div class="score-badge">🎉 Quiz Completed!&nbsp;&nbsp;Score: {st.session_state.score} / {len(questions)}</div>',
            unsafe_allow_html=True
        )
        st.write("")

        if st.button("🔄 Restart Quiz"):
            for key in ["quiz_mode", "questions", "answers", "current_q", "score",
                        "show_feedback", "last_result", "selected_option", "score_updated"]:
                st.session_state[key] = (
                    False if key in ("quiz_mode", "show_feedback", "score_updated")
                    else [] if key in ("questions", "answers")
                    else 0 if key in ("current_q", "score")
                    else None
                )
            st.rerun()