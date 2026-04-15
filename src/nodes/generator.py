from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings 
import re
import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ✅ FIX: support both local + cloud
groq_api_key = os.getenv("GROQ_API_KEY") or st.secrets["GROQ_API_KEY"]

# 🔥 Groq LLM (FAST)
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=groq_api_key
)

# 🔥 Embeddings for inline citation
embedder = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# =========================
# 🧠 TONE SYSTEM
# =========================
TONE_MAP = {
    "simple": """
Explain in a very simple, beginner-friendly way.
- Use easy words
- Avoid technical jargon
- Use analogies if possible
- Keep it short and clear
""",
    "beginner": """
Explain step-by-step with basic concepts and minimal jargon.
""",
    "interview": """
Give a crisp, structured answer suitable for system design interviews.
Focus on clarity and key points.
""",
    "deep": """
Provide a detailed, technical deep dive with advanced insights.
""",
    "concise": """
Keep the answer short and to the point.
""",
    "default": """
Explain in a professional system design manner.
- Include technical depth
- Focus on real-world system behavior
"""
}


def detect_tone(query: str):
    q = query.lower()

    if any(x in q for x in ["simple", "easily", "like i'm 5"]):
        return "simple"
    elif "beginner" in q:
        return "beginner"
    elif "interview" in q:
        return "interview"
    elif any(x in q for x in ["deep", "detailed", "advanced"]):
        return "deep"
    elif any(x in q for x in ["short", "concise"]):
        return "concise"
    else:
        return "default"


# =========================
# 🧪 MCQ COUNT (UPDATED)
# =========================
def get_mcq_count(query: str):
    q = query.lower()

    if any(x in q for x in ["quiz", "mcq", "test"]):
        return 10

    return 0


# =========================
# 🔥 CLEAN NUMBERING
# =========================
def clean_numbering(text: str):
    lines = text.split("\n")
    cleaned = []

    for line in lines:
        line = line.strip()

        if re.match(r'^\d+\.$', line):
            continue

        cleaned.append(line)

    return "\n".join(cleaned)


# =========================
# 🧪 SINGLE MCQ
# =========================
def generate_mcq(query, documents):
    print("🧪 Generating MCQ...")

    documents = sorted(
        documents,
        key=lambda x: len(x.page_content),
        reverse=True
    )[:4]

    context = "\n\n".join([doc.page_content for doc in documents])

    prompt = f"""
You are a system design expert.

Generate ONE multiple-choice question STRICTLY based on the USER QUERY.

STRICT RULES:
- DO NOT add any introduction
- START directly with Question

FORMAT:

Question:
<question>

Options:
A. <option>
B. <option>
C. <option>
D. <option>

Correct Answer: <A/B/C/D>
Explanation: <1–2 line explanation>

Context:
{context}
"""

    response = llm.invoke(prompt)
    text = response.content.strip()

    text = re.sub(r'^.*?(Question\s*:)', r'\1', text, flags=re.IGNORECASE | re.DOTALL)

    lines = text.split("\n")

    visible_lines = []
    correct = ""
    explanation = ""

    for line in lines:
        if line.startswith("Correct Answer:"):
            correct = line.replace("Correct Answer:", "").strip()
        elif line.startswith("Explanation:"):
            explanation = line.replace("Explanation:", "").strip()
        else:
            visible_lines.append(line)

    visible = clean_numbering("\n".join(visible_lines).strip())

    if not correct:
        correct = "A"
    if not explanation:
        explanation = "Explanation not generated."

    hidden = f"ANSWER:{correct}|EXPLANATION:{explanation}"

    return "__MCQ__\n" + visible + "\n\n__HIDDEN__\n" + hidden


# =========================
# 🧪 MULTI MCQ (FINAL FIX 🔥)
# =========================
def generate_mcq_batch(query, documents, count):
    print(f"🧪 Generating {count} MCQs...")

    documents = sorted(
        documents,
        key=lambda x: len(x.page_content),
        reverse=True
    )[:4]

    context = "\n\n".join([doc.page_content for doc in documents])

    prompt = f"""
Generate EXACTLY {count} multiple-choice questions.

STRICT RULES:
- NO introduction
- START directly with numbered questions (1., 2., 3., ...)
- DO NOT add extra text

FORMAT:

1. <question>
Options:
A. ...
B. ...
C. ...
D. ...

Correct Answer: <A/B/C/D>
Explanation: <short>

Context:
{context}
"""

    response = llm.invoke(prompt)
    text = response.content.strip()

    text = re.sub(r'^.*?(\d+\.)', r'\1', text, flags=re.DOTALL)

    raw_blocks = re.split(r'(?:\n|^)\s*\d+\.\s+', text)

    blocks = [b.strip() for b in raw_blocks if len(b.strip()) > 30]
    blocks = blocks[:count]

    visible_blocks = []
    hidden_blocks = []

    for block in blocks:
        lines = block.split("\n")

        visible_lines = []
        correct = ""
        explanation = ""

        for line in lines:
            if line.startswith("Correct Answer:"):
                correct = line.replace("Correct Answer:", "").strip()
            elif line.startswith("Explanation:"):
                explanation = line.replace("Explanation:", "").strip()
            else:
                visible_lines.append(line)

        visible_clean = clean_numbering("\n".join(visible_lines).strip())

        hidden = f"ANSWER:{correct}|EXPLANATION:{explanation}"

        visible_blocks.append(visible_clean)
        hidden_blocks.append(hidden)

    return "__MCQ__\n" + "\n\n---\n\n".join(visible_blocks) + "\n\n__HIDDEN__\n" + "||".join(hidden_blocks)


# =========================
# 🧪 MCQ EVALUATION
# =========================
def evaluate_mcq(hidden_answer, user_choice):
    try:
        parts = hidden_answer.split("|")

        correct = parts[0].replace("ANSWER:", "").strip()
        explanation = parts[1].replace("EXPLANATION:", "").strip()

        correct = correct.split(".")[0].strip().upper()

    except:
        return "❌ Error evaluating answer."

    user_choice = user_choice.strip().upper()

    if user_choice == correct:
        return f"✅ Correct!\nExplanation: {explanation}"
    else:
        return f"❌ Incorrect\nCorrect Answer: {correct}\nExplanation: {explanation}"


# =========================
# 🔥 SEMANTIC MATCH
# =========================
def get_best_doc_index(sentence, doc_embeddings):
    sent_emb = embedder.embed_query(sentence)

    scores = []
    for emb in doc_embeddings:
        score = sum(a * b for a, b in zip(sent_emb, emb))
        scores.append(score)

    return scores.index(max(scores))


# =========================
# 🚀 MAIN GENERATOR
# =========================
def generate_answer(query, documents):
    print("🤖 Generating answer...")

    mcq_count = get_mcq_count(query)

    if mcq_count == 1:
        return generate_mcq(query, documents)

    if mcq_count > 1:
        return generate_mcq_batch(query, documents, mcq_count)

    tone = detect_tone(query)
    style_instruction = TONE_MAP.get(tone, TONE_MAP["default"])

    documents = sorted(
        documents,
        key=lambda x: len(x.page_content),
        reverse=True
    )[:4]

    context = "\n\n".join([doc.page_content for doc in documents])

    if len(context.strip()) < 100:
        return "I couldn't find enough relevant information  to answer this question."

    prompt = f"""
You are a senior Staff-level System Design engineer.

STRICT RULES:
- Use ONLY the provided context
- Do NOT use prior knowledge

⚠️ IMPORTANT:
If the user's query is unclear, vague, or incomplete:
- DO NOT assume the system
- DO NOT generate a full system design answer
- Instead, ask the user to clarify their question

---

Answer Guidelines:
{style_instruction}

---

Context:
{context}

Question:
{query}

Answer:
"""


    response = llm.invoke(prompt)
    answer_text = response.content.strip()

    # ✅ NEW BLOCK HERE
    answer_lower = answer_text.lower()

    if (
        "clarify" in answer_lower
        or "unclear" in answer_lower
        or "not clear" in answer_lower
        or "need more context" in answer_lower
        or "assum" in answer_lower
        or len(answer_text.split()) < 40
    ):
        return answer_text

    docs = documents[:3]
    doc_embeddings = [embedder.embed_query(doc.page_content) for doc in docs]

    paragraphs = answer_text.split("\n\n")

    used_sources = {}
    final_paragraphs = []

    for para in paragraphs:
        p = para.strip()
        if not p:
            continue

        idx = get_best_doc_index(p, doc_embeddings)

        meta = docs[idx].metadata if hasattr(docs[idx], "metadata") else {}

        url = meta.get("source")
        title = meta.get("title", "Source")

        if url and url not in used_sources:
            used_sources[url] = title

        final_paragraphs.append(p)

    sources_text = "\n".join([
        f"🔗 [{title}]({url})"
        for url, title in used_sources.items()
    ])

    return "\n\n".join(final_paragraphs) + "\n\n📚 Sources:\n" + sources_text

 
# 🔥 FOLLOW-UPS
# =========================
def generate_followups(answer):
    prompt = f"""
Generate EXACTLY 2 short follow-up questions.

Rules:
- Only return questions
- No numbering
- Each question MUST be on a new line
- No extra text

Answer:
{answer}
"""

    response = llm.invoke(prompt)
    text = response.content.strip()

    lines = re.split(r'\n|\d+\.', text)

    cleaned = []
    for line in lines:
        line = line.strip("- ").strip()

        if len(line) > 10 and "?" in line:
            cleaned.append(line)

        if len(cleaned) == 2:
            break

    if len(cleaned) < 2:
        cleaned = [
            "What are the key challenges in this system?",
            "How can this system be optimized for scale?"
        ]

    return cleaned