from langchain_ollama import ChatOllama
import json

# Smart model for evaluation
llm = ChatOllama(model="qwen2.5:7b")

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