from langchain_groq import ChatGroq
import os
import streamlit as st
import json

# Load API key (works locally + Streamlit Cloud)
groq_api_key = os.getenv("GROQ_API_KEY") or st.secrets["GROQ_API_KEY"]

# Smart model for evaluation (using Groq instead of Ollama)
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=groq_api_key
)


def critic_answer(query, answer):
    print("🧠 Evaluating answer...")

    prompt = f"""
    You are an AI evaluator.

    Evaluate the following answer:

    Question: {query}
    Answer: {answer}

    Check:
    - Is it correct?
    - Is it complete?
    - Is it relevant?

    Return ONLY JSON:
    {{
        "score": 0-10,
        "feedback": "short feedback"
    }}
    """

    response = llm.invoke(prompt)

    try:
        result = json.loads(response.content)
    except:
        result = {
            "score": 5,
            "feedback": response.content
        }

    return result