from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

def test_retrieval():
    print("🔍 Testing retrieval...")

    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    db = Chroma(
        persist_directory="db",
        embedding_function=embeddings
    )

    retriever = db.as_retriever(search_kwargs={"k": 3})

    query = input("Enter your query: ")

    # ✅ FIXED LINE (new LangChain API)
    docs = retriever.invoke(query)

    print("\n📄 Top Results:\n")

    for i, doc in enumerate(docs):
        print(f"--- Result {i+1} ---")
        print(doc.page_content[:300])
        print("\n")

if __name__ == "__main__":
    test_retrieval()