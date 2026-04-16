from langgraph.graph import StateGraph

from src.models import RAGState
from src.nodes.generator import generate_answer
from src.nodes.critic import critic_answer
from src.nodes.refiner import refine_answer

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


# ✅ SAME embedding as ingestion
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ✅ FIX: Explicit collection name (IMPORTANT)
db = Chroma(
    persist_directory="db",
    embedding_function=embeddings,
    collection_name="langchain"  # 🔥 ensures correct loading
)

# ✅ IMPROVED retrieval
retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)


# 🔹 Nodes

def retrieve_node(state: RAGState):
    print("📥 Retrieving documents...")

    docs = retriever.invoke(state.query)

    # ✅ FIX: Less aggressive filtering
    clean_docs = [
        doc for doc in docs
        if doc.page_content.strip()
    ]

    print(f"✅ Retrieved {len(clean_docs)} docs")

    return {"documents": clean_docs}


def generate_node(state: RAGState):
    answer = generate_answer(state.query, state.documents)

    # 🔥 If MCQ → skip critic & refine
    if "__MCQ__" in answer:
        return {
            "answer": answer,
            "iteration": state.max_iterations
        }

    return {"answer": answer}


def critic_node(state: RAGState):
    critique = critic_answer(state.query, state.answer)
    return {"critique": critique}


def refine_node(state: RAGState):
    answer = refine_answer(
        state.query,
        state.answer,
        state.critique["feedback"]
    )
    return {
        "answer": answer,
        "iteration": state.iteration + 1
    }


# 🔹 Decision logic

def should_continue(state: RAGState):
    if state.critique.get("score", 0) >= 7:
        return "end"

    if state.iteration >= 1:
        return "end"

    return "refine"


# 🔹 Build Graph

graph = StateGraph(RAGState)

graph.add_node("retrieve", retrieve_node)
graph.add_node("generate", generate_node)
graph.add_node("critic", critic_node)
graph.add_node("refine", refine_node)

graph.set_entry_point("retrieve")

graph.add_edge("retrieve", "generate")
graph.add_edge("generate", "critic")

graph.add_conditional_edges(
    "critic",
    should_continue,
    {
        "refine": "refine",
        "end": "__end__"
    }
)

graph.add_edge("refine", "generate")

app = graph.compile()