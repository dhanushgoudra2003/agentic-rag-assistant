from langchain_groq import ChatGroq
import os
import streamlit as st

# Load API key
groq_api_key = os.getenv("GROQ_API_KEY") or st.secrets["GROQ_API_KEY"]

# Use Groq instead of Ollama
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=groq_api_key
)


def refine_answer(query, answer, feedback):
    print("🔧 Refining answer...")

    prompt = f"""
    Improve the answer based on feedback.

    Question: {query}
    Answer: {answer}
    Feedback: {feedback}

    Give a better, corrected answer.
    """

    response = llm.invoke(prompt)

    return response.content