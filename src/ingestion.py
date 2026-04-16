from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

def ingest_docs():
    print("🚀 Starting ingestion...")

    docs = []

    for file in os.listdir("data/docs"):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(f"data/docs/{file}")
            docs.extend(loader.load())

    print(f"Loaded {len(docs)} documents")

    if len(docs) == 0:
        print("❌ No PDFs found in data/docs")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(docs)

    print(f"Created {len(chunks)} chunks")

    # ✅ FIXED: Use HuggingFace instead of Ollama
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory="db"
    )

    print("✅ Ingestion complete!")

if __name__ == "__main__":
    ingest_docs()