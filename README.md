# 🚀 AI System Design Assistant (Agentic RAG)

An intelligent **System Design Assistant** powered by **Agentic RAG (Retrieval-Augmented Generation)** that answers system design questions using **PDFs + Web URLs + LLM reasoning**.

🔗 **Live Demo:**  
👉 https://agentic-rag-assistant-hudng2zjumk6mkezxjycru.streamlit.app/

---

# 🧠 What is this?

This project is not just a chatbot.

It is an **Agentic RAG System** that:
- Retrieves knowledge from **PDFs and Web URLs**
- Uses **LLM reasoning (Generate → Critic → Refine)**
- Produces high-quality system design answers
- Supports **quiz generation (MCQs)**

---

# ✨ Features

## 🔍 Multi-Source Retrieval
- 📄 PDFs (local documents)
- 🌐 Web URLs
- 📦 Chroma Vector Database

## 🤖 Agentic Workflow
Pipeline:
Retrieve → Generate → Critic → Refine

- Generator → generates answer  
- Critic → evaluates quality  
- Refiner → improves answer  

## 🧠 Smart Retrieval
- Semantic search using embeddings  
- Keyword-based boosting  
- Top-k ranking  

## 📝 Quiz Mode
- Generate MCQs on:
  - Caching
  - Distributed Systems
  - System Design

## ⚡ Fast Responses
- Powered by **Groq (LLaMA 3.1)**  

---

# 🏗️ Architecture

User Query  
↓  
Retriever (Chroma DB)  
↓  
Relevant Documents (PDF + URLs)  
↓  
Generator (LLM)  
↓  
Critic (LLM)  
↓  
Refiner (LLM)  
↓  
Final Answer  

---

# 🛠️ Tech Stack

- Frontend: Streamlit  
- LLM: Groq (LLaMA 3.1)  
- Framework: LangChain + LangGraph  
- Vector DB: ChromaDB  
- Embeddings: Sentence Transformers (MiniLM)  
- Data: PDFs + URLs  
- Deployment: Streamlit Cloud  

---

# 📂 Project Structure

agentic-rag-assistant/
│
├── app.py
├── requirements.txt
├── db/
├── data/
│   ├── docs/
│   └── urls.txt
│
├── src/
│   ├── graph.py
│   ├── ingestion.py
│   ├── models.py
│   └── nodes/
│       ├── generator.py
│       ├── critic.py
│       └── refiner.py

---

# ⚙️ Setup & Installation

## 1. Clone Repo
git clone https://github.com/your-username/agentic-rag-assistant.git  
cd agentic-rag-assistant  

## 2. Create Virtual Environment
python -m venv venv  
venv\Scripts\activate  

## 3. Install Dependencies
pip install -r requirements.txt  

## 4. Add API Key
Create `.env` file:
GROQ_API_KEY=your_api_key_here  

## 5. Run Ingestion
python src/ingestion.py  

## 6. Run App
streamlit run app.py  

---

# 📥 Data Ingestion

## PDFs
Place files in:
data/docs/

## URLs
Add in:
data/urls.txt

Example:
https://redis.io/docs/  
https://systemdesignprimer.com/  

---

# 🧪 Example Queries

Design a URL shortener like bit.ly  
Explain caching strategies (LRU, LFU)  
How does Redis work internally?  
Give me 5 MCQs on caching  

---

# 🚀 Deployment

1. Push code to GitHub  
2. Connect repo to Streamlit Cloud  
3. Add GROQ_API_KEY in secrets  
4. Deploy  

---


# ⭐ Support

If you like this project:
⭐ Star the repo  
🔗 Share it  
💬 Give feedback  

---

# 💡 Note

This project demonstrates:
- Agentic AI workflows  
- RAG architecture  
- Multi-source retrieval  
- Production deployment  
