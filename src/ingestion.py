from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

def ingest_docs():
    print("🚀 Starting ingestion...")

    docs = []

    # ✅ Load PDFs
    for file in os.listdir("data/docs"):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(f"data/docs/{file}")
            docs.extend(loader.load())

    print(f"Loaded {len(docs)} PDF documents")

    # ✅ Load URLs (🔥 FIXED PATH)
    if os.path.exists("processed_urls.txt"):
        with open("processed_urls.txt", "r") as f:
            urls = [line.strip() for line in f.readlines() if line.strip()]

        url_loader = WebBaseLoader(urls)
        url_docs = url_loader.load()

        print(f"Loaded {len(url_docs)} URL documents")

        docs.extend(url_docs)
    else:
        print("❌ processed_urls.txt not found")

    # ❌ No data
    if len(docs) == 0:
        print("❌ No data found")
        return

    # ✅ Split
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(docs)

    print(f"Created {len(chunks)} chunks")

    # ✅ Embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # 🔥 IMPORTANT: Delete old DB before creating new one
    if os.path.exists("db"):
        import shutil
        shutil.rmtree("db")

    db = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory="db"
    )

    print("✅ Ingestion complete!")

if __name__ == "__main__":
    ingest_docs()