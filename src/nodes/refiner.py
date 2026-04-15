from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.2:3b")

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